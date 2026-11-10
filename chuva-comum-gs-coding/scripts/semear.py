"""Execute com python -m scripts.semear. Somente dados sintéticos."""
from app.config import load_config
from app.repository import OccurrenceRepository
from mysql.connector import Error

SAMPLES = [
    {'cidade': 'sao-paulo', 'bairro': 'Setor Norte', 'tipo': 'alagamento',
     'gravidade': 'alta', 'status': 'aberta'},
    {'cidade': 'sao-paulo', 'bairro': 'Setor Central', 'tipo': 'bueiro_obstruido',
     'gravidade': 'media', 'status': 'em_analise'},
    {'cidade': 'sao-paulo', 'bairro': 'Setor Sul', 'tipo': 'via_interditada',
     'gravidade': 'baixa', 'status': 'resolvida'},
    {'cidade': 'porto-alegre', 'bairro': 'Setor Norte', 'tipo': 'alagamento',
     'gravidade': 'alta', 'status': 'em_analise'},
    {'cidade': 'recife', 'bairro': 'Setor Central', 'tipo': 'bueiro_obstruido',
     'gravidade': 'media', 'status': 'aberta'},
]


def main():
    repo = OccurrenceRepository(load_config())
    _, total = repo.list({'pagina': 1, 'limite': 1})
    if total:
        print('Banco já contém registros; nenhuma amostra adicionada.')
        return
    for sample in SAMPLES:
        repo.create(sample)
    print('Cinco ocorrências fictícias criadas. Nenhum incidente real foi registrado.')


if __name__ == '__main__':
    try:
        main()
    except Error:
        raise SystemExit('Banco indisponível. Confirme .env e docker compose up -d --wait db.') from None
