import os

from app.audit import create_logger
from app.config import load_config
from app.repository import OccurrenceRepository
from app.tcp_service import SummaryServer


def main():
    config = load_config()
    address = (os.getenv('TCP_HOST', '127.0.0.1'), int(os.getenv('TCP_PORT', '5050')))
    with SummaryServer(address, config['TCP_TOKEN'], OccurrenceRepository(config),
                       create_logger(config['LOG_PATH'])) as server:
        print(f'Consulta TCP local em {address[0]}:{address[1]}. Ctrl+C encerra.')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
