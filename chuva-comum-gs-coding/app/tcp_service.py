"""JSON delimitado por newline: um pedido por conexão, no máximo 1024 bytes."""
import json
import socket
import socketserver

from .audit import audit
from .security import valid_token

MAX_FRAME = 1024


def read_frame(sock):
    buffer = bytearray()
    while b'\n' not in buffer:
        chunk = sock.recv(min(256, MAX_FRAME + 1 - len(buffer)))
        if not chunk:
            raise ValueError('Mensagem incompleta')
        buffer.extend(chunk)
        if len(buffer) > MAX_FRAME:
            raise ValueError('Mensagem excessiva')
    frame, rest = bytes(buffer).split(b'\n', 1)
    if rest.strip():
        raise ValueError('Somente um pedido por conexão')
    return json.loads(frame.decode('utf-8'))


class SummaryHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(2)
        result = 'falha'
        try:
            data = read_frame(self.request)
            if not isinstance(data, dict) or set(data) != {'acao', 'token'} or data['acao'] != 'resumo':
                response = {'erro': 'Mensagem inválida.'}
            elif not valid_token(data['token'], self.server.token):
                response = {'erro': 'Credencial inválida.'}
            else:
                response = {'dados': self.server.repository.summary()}
                result = 'sucesso'
        except (ValueError, UnicodeError, socket.timeout):
            response = {'erro': 'Mensagem inválida ou tempo excedido.'}
        except Exception:
            response = {'erro': 'Serviço temporariamente indisponível.'}
        try:
            self.request.sendall((json.dumps(response, ensure_ascii=False) + '\n').encode('utf-8'))
        except OSError:
            result = 'conexao_encerrada'
        audit(self.server.logger, 'tcp.resumo', result)


class SummaryServer(socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, address, token, repository, logger):
        if address[0] not in ('127.0.0.1', '::1'):
            raise ValueError('O módulo didático TCP só pode escutar em loopback.')
        if address[0] == '::1':
            self.address_family = socket.AF_INET6
        self.token, self.repository, self.logger = token, repository, logger
        super().__init__(address, SummaryHandler)
