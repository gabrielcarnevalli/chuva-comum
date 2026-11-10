from pathlib import Path

import pytest
from mysql.connector import Error

from app.weather import WeatherUnavailable


@pytest.mark.parametrize('method,path', [('post', '/api/ocorrencias'),
                                       ('put', '/api/ocorrencias/7'), ('delete', '/api/ocorrencias/7')])
def test_mutation_requires_token(client, method, path):
    response = getattr(client, method)(path, json={})
    assert response.status_code == 401
    assert response.headers['WWW-Authenticate'] == 'Bearer'


@pytest.mark.parametrize('payload', [None, [], {}, {'cidade': {'$ne': None}},
                                    {'cidade': "' OR 1=1 --"}, {'cpf': '123'}])
def test_rejects_invalid_payload(client, headers, payload):
    response = client.post('/api/ocorrencias', data=__import__('json').dumps(payload),
                           content_type='application/json', headers=headers)
    assert response.status_code == 400


@pytest.mark.parametrize('field,value', [('cidade', "' OR 1=1 --"), ('tipo', '<script>alert(1)</script>'),
                                       ('bairro', 'Nome de pessoa'), ('gravidade', 1), ('status', None)])
def test_each_field_is_validated(client, headers, sample, field, value):
    assert client.post('/api/ocorrencias', json={**sample, field: value}, headers=headers).status_code == 400


@pytest.mark.parametrize('query', ['cidade=qualquer', 'limite=101', 'pagina=0', 'pagina=-1',
                                 'limite=1.5', 'id=99999999999999999', 'status=aberta&status=resolvida',
                                 'q=teste', 'cidade=%27%20OR%201=1--', 'pagina=１'])
def test_rejects_invalid_filters(client, query):
    assert client.get('/api/ocorrencias?' + query).status_code == 400


def test_create_and_location(client, headers, sample):
    response = client.post('/api/ocorrencias', headers=headers, json=sample)
    assert response.status_code == 201
    assert response.headers['Location'] == '/api/ocorrencias?id=7'


def test_update_delete_and_not_found(app, client, headers, sample):
    assert client.put('/api/ocorrencias/7', headers=headers, json=sample).status_code == 200
    app.extensions['repository'].update.return_value = None
    assert client.put('/api/ocorrencias/99', headers=headers, json=sample).status_code == 404
    response = client.delete('/api/ocorrencias/7', headers=headers)
    assert response.status_code == 204 and response.data == b''
    app.extensions['repository'].delete.return_value = False
    assert client.delete('/api/ocorrencias/99', headers=headers).status_code == 404


def test_bad_json_type_size_and_path(client, headers):
    assert client.post('/api/ocorrencias', headers=headers, data='{', content_type='application/json').status_code == 400
    assert client.post('/api/ocorrencias', headers=headers, data='texto').status_code == 415
    assert client.post('/api/ocorrencias', headers=headers, data='x' * 5000,
                       content_type='application/json').status_code == 413
    assert client.delete('/api/ocorrencias/0', headers=headers).status_code == 400
    assert client.delete('/api/ocorrencias/7?x=1', headers=headers).status_code == 400
    assert client.delete('/api/ocorrencias/7', headers=headers, data='x').status_code == 400


def test_error_details_never_leak(app, client):
    app.extensions['repository'].list.side_effect = Error('password=SEGREDO db.host INTERNO')
    response = client.get('/api/ocorrencias')
    assert response.status_code == 503
    assert b'SEGREDO' not in response.data and b'INTERNO' not in response.data
    app.extensions['repository'].list.side_effect = RuntimeError('pilha secreta')
    response = client.get('/api/ocorrencias')
    assert response.status_code == 500 and b'pilha' not in response.data


def test_weather_failure_is_explicit(app, client):
    app.extensions['weather'].get.side_effect = WeatherUnavailable()
    assert client.get('/api/clima?cidade=sao-paulo').status_code == 503
    assert client.get('/api/clima?cidade=http://127.0.0.1').status_code == 400
    assert client.get('/api/clima?cidade=recife&url=http://localhost').status_code == 400


def test_headers_and_audit_do_not_store_token(app, client, headers, sample):
    response = client.post('/api/ocorrencias', headers=headers, json=sample)
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert "script-src 'self'" in response.headers['Content-Security-Policy']
    assert 'Access-Control-Allow-Origin' not in response.headers
    content = Path(app.config['LOG_PATH']).read_text()
    assert 'create_occurrence' in content and '201' in content and 'Z ' in content
    assert headers['Authorization'] not in content and 'Setor Norte' not in content


def test_rate_limit(client):
    for _ in range(120):
        assert client.get('/api/ocorrencias').status_code == 200
    response = client.get('/api/ocorrencias')
    assert response.status_code == 429 and response.headers['Retry-After'] == '60'


def test_html_and_method(client):
    response = client.get('/')
    assert response.status_code == 200 and b'ChuvaComum' in response.data
    response = client.patch('/api/ocorrencias')
    assert response.status_code == 405 and 'GET' in response.headers['Allow']
    assert client.get('/api/nao-existe').status_code == 404
