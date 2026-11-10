import json
import os
import socket

from app.config import load_config
from app.tcp_service import read_frame


def main():
    config = load_config()
    host = os.getenv('TCP_HOST', '127.0.0.1')
    if host not in ('127.0.0.1', '::1'):
        raise SystemExit('Cliente didático limitado a loopback.')
    try:
        with socket.create_connection((host, int(os.getenv('TCP_PORT', '5050'))), timeout=4) as sock:
            packet = {'acao': 'resumo', 'token': config['TCP_TOKEN']}
            sock.sendall((json.dumps(packet) + '\n').encode())
            print(json.dumps(read_frame(sock), indent=2, ensure_ascii=False))
    except (OSError, ValueError):
        raise SystemExit('Consulta indisponível. Confirme que tcp_server.py está em execução.') from None


if __name__ == '__main__':
    main()
