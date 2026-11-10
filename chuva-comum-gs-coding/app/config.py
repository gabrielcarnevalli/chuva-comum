"""Configuração local. Nenhum segredo tem valor padrão no código."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def load_config():
    load_dotenv(ROOT / '.env')
    required = ('DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'ADMIN_TOKEN', 'TCP_TOKEN')
    if any(not os.getenv(key) or os.getenv(key).startswith('SUBSTITUIR') for key in required):
        raise RuntimeError('Configuração incompleta. Execute python scripts/configurar.py.')
    if any(len(os.environ[key]) < 32 for key in ('ADMIN_TOKEN', 'TCP_TOKEN')):
        raise RuntimeError('Tokens devem ter ao menos 32 caracteres.')
    if os.environ['ADMIN_TOKEN'] == os.environ['TCP_TOKEN']:
        raise RuntimeError('Use tokens diferentes para HTTP e TCP.')
    return {
        'DB_HOST': os.environ['DB_HOST'], 'DB_PORT': int(os.getenv('DB_PORT', '3307')),
        'DB_NAME': os.environ['DB_NAME'], 'DB_USER': os.environ['DB_USER'],
        'DB_PASSWORD': os.environ['DB_PASSWORD'], 'ADMIN_TOKEN': os.environ['ADMIN_TOKEN'],
        'TCP_TOKEN': os.environ['TCP_TOKEN'],
        'LOG_PATH': str(ROOT / os.getenv('LOG_PATH', 'logs/auditoria.log')),
        'MAX_CONTENT_LENGTH': 4096,
    }
