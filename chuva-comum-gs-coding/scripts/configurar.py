"""Gera segredos locais; não sobrescreve configuração existente."""
from pathlib import Path
import os
import secrets

ROOT = Path(__file__).resolve().parents[1]


def main():
    template = (ROOT / '.env.example').read_text(encoding='utf-8')
    for key in ('MYSQL_ROOT_PASSWORD', 'DB_PASSWORD', 'ADMIN_TOKEN', 'TCP_TOKEN'):
        lines = template.splitlines()
        template = '\n'.join(
            f'{key}={secrets.token_urlsafe(36)}' if line.startswith(key + '=') else line
            for line in lines
        ) + '\n'
    try:
        fd = os.open(ROOT / '.env', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        print('.env já existe; preservado. Nenhuma senha foi alterada.')
        return
    with os.fdopen(fd, 'w', encoding='utf-8') as file:
        file.write(template)
    print('.env criado. Segredos não foram exibidos. Abra-o apenas localmente.')


if __name__ == '__main__':
    main()
