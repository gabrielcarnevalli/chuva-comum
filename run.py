"""Servidor WSGI local, sem debugger/reloader e sem acesso externo por padrão."""
import os

from waitress import serve

from app import create_app


if __name__ == '__main__':
    app = create_app()
    serve(app, host=os.getenv('APP_HOST', '127.0.0.1'), port=int(os.getenv('APP_PORT', '5000')),
          threads=4, max_request_body_size=4096, clear_untrusted_proxy_headers=True)
