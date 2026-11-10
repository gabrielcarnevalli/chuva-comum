"""Entrega somente arquivos previstos, excluindo segredos, caches e banco."""
import argparse
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {'.env.example', '.gitignore', 'README.md', 'requirements.txt', 'requirements-dev.txt',
              'compose.yaml', 'pyproject.toml', 'run.py', 'tcp_server.py', 'tcp_client.py'}
DIRECTORIES = {'app', 'sql', 'scripts', 'tests', 'docs'}
EXCLUDED = {'__pycache__', '.pytest_cache', '.ruff_cache', '.git', '.venv', 'htmlcov'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT.parent / 'chuva-comum-gs.zip')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with zipfile.ZipFile(args.output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ROOT.rglob('*')):
            if not path.is_file() or path.is_symlink():
                continue
            relative = path.relative_to(ROOT)
            if any(part in EXCLUDED for part in relative.parts):
                continue
            if path.name.startswith('.env') and relative.as_posix() != '.env.example':
                continue
            if path.suffix in {'.zip', '.pyc', '.log'}:
                continue
            if (len(relative.parts) == 1 and relative.name in ROOT_FILES
                    or relative.parts[0] in DIRECTORIES
                    or relative.as_posix() == 'logs/.gitkeep'):
                archive.write(path, 'chuva-comum/' + relative.as_posix())
                count += 1
    checksum = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.output.with_suffix('.zip.sha256').write_text(f'{checksum}  {args.output.name}\n', encoding='utf-8')
    print(f'Pacote criado: {args.output.name}, {count} arquivos, sem .env ou banco.')


if __name__ == '__main__':
    main()
