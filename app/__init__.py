"""Fábrica Flask. Quatro operações CRUD e uma consulta meteorológica auxiliar."""
from flask import Flask, g, jsonify, render_template, request
from mysql.connector import Error as MySQLError
from werkzeug.exceptions import HTTPException

from .audit import audit, create_logger
from .config import load_config
from .repository import OccurrenceRepository
from .security import RateLimiter, valid_token
from .validation import CITIES, ValidationError, list_params, occurrence_payload, positive_integer
from .weather import WeatherService, WeatherUnavailable


def create_app(config=None, repository=None, weather=None):
    app = Flask(__name__)
    app.config.update(config if config is not None else load_config())
    app.config.setdefault('MAX_CONTENT_LENGTH', 4096)
    logger = create_logger(app.config['LOG_PATH'])
    repo = repository if repository is not None else OccurrenceRepository(app.config)
    weather = weather if weather is not None else WeatherService(logger)
    limiter = RateLimiter()
    app.extensions.update(repository=repo, weather=weather, audit=logger, limiter=limiter)

    def error(message, status):
        return jsonify(erro=message), status

    @app.before_request
    def protect_api():
        if not request.path.startswith('/api/'):
            return None
        if not limiter.allow(request.remote_addr or 'local'):
            response, status = error('Muitas requisições. Tente novamente em um minuto.', 429)
            response.headers['Retry-After'] = '60'
            return response, status
        if request.method in ('POST', 'PUT', 'DELETE'):
            header = request.headers.get('Authorization', '')
            if not header.startswith('Bearer ') or not valid_token(header[7:], app.config['ADMIN_TOKEN']):
                response, status = error('Credencial ausente ou inválida.', 401)
                response.headers['WWW-Authenticate'] = 'Bearer'
                return response, status
        return None

    @app.after_request
    def finalize(response):
        response.headers.update({
            'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY',
            'Referrer-Policy': 'no-referrer', 'Cache-Control': 'no-store',
            'Permissions-Policy': 'geolocation=(), camera=(), microphone=()',
            'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self'; "
                                       "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; "
                                       "base-uri 'none'; form-action 'self'; object-src 'none'",
        })
        if request.path.startswith('/api/'):
            # Endpoint é constante; nunca registrar URL/corpo potencialmente malicioso.
            audit(logger, request.endpoint or 'rota.desconhecida', response.status_code,
                  metodo=request.method, **getattr(g, 'audit_metadata', {}))
        return response

    @app.get('/')
    def index():
        return render_template('index.html')

    @app.get('/api/ocorrencias')
    def list_occurrences():
        filters = list_params(request.args)
        items, total = repo.list(filters)
        return jsonify(dados=items, total=total, pagina=filters['pagina'], limite=filters['limite'])

    def payload():
        if request.args:
            raise ValidationError('Esta operação não aceita parâmetros de consulta.')
        if not request.is_json:
            return None
        return occurrence_payload(request.get_json())

    @app.post('/api/ocorrencias')
    def create_occurrence():
        data = payload()
        if data is None:
            return error('Use Content-Type application/json.', 415)
        item = repo.create(data)
        g.audit_metadata = {'id': item['id']}
        response = jsonify(dados=item)
        response.status_code = 201
        response.headers['Location'] = f"/api/ocorrencias?id={item['id']}"
        return response

    @app.put('/api/ocorrencias/<occurrence_id>')
    def update_occurrence(occurrence_id):
        occurrence_id = positive_integer(occurrence_id, 'id')
        data = payload()
        if data is None:
            return error('Use Content-Type application/json.', 415)
        item = repo.update(occurrence_id, data)
        if item is None:
            return error('Ocorrência não encontrada.', 404)
        g.audit_metadata = {'id': occurrence_id}
        return jsonify(dados=item)

    @app.delete('/api/ocorrencias/<occurrence_id>')
    def delete_occurrence(occurrence_id):
        occurrence_id = positive_integer(occurrence_id, 'id')
        if request.args or request.get_data():
            raise ValidationError('DELETE não aceita parâmetros nem corpo.')
        if not repo.delete(occurrence_id):
            return error('Ocorrência não encontrada.', 404)
        g.audit_metadata = {'id': occurrence_id}
        return '', 204

    @app.get('/api/clima')
    def get_weather():
        if (set(request.args) != {'cidade'} or len(request.args.getlist('cidade')) != 1
                or request.args['cidade'] not in CITIES):
            raise ValidationError('Informe uma cidade atendida, sem parâmetros adicionais.')
        return jsonify(dados=weather.get(request.args['cidade']))

    @app.errorhandler(ValidationError)
    def invalid_input(exc):
        return error(str(exc), 400)

    @app.errorhandler(WeatherUnavailable)
    def weather_failure(exc):
        return error('Previsão indisponível. Consulte os canais oficiais.', 503)

    @app.errorhandler(MySQLError)
    def database_failure(exc):
        return error('Serviço de dados temporariamente indisponível.', 503)

    @app.errorhandler(HTTPException)
    def http_error(exc):
        messages = {400: 'JSON ou requisição inválida.', 404: 'Recurso não encontrado.',
                    405: 'Método não permitido.', 413: 'Corpo da requisição excede 4 KB.',
                    415: 'Use Content-Type application/json.'}
        response, status = error(messages.get(exc.code, 'Requisição não permitida.'), exc.code)
        if exc.code == 405 and exc.valid_methods:
            response.headers['Allow'] = ', '.join(exc.valid_methods)
        return response, status

    @app.errorhandler(Exception)
    def unexpected_error(exc):
        audit(logger, 'erro.interno', 'falha')
        return error('Não foi possível concluir a operação.', 500)

    return app
