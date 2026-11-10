"""Demonstra os quatro verbos via HTTP real; não exibe credenciais."""
import requests

from app.config import load_config
from scripts.semear import SAMPLES


def main():
    config = load_config()
    base = 'http://127.0.0.1:5000/api/ocorrencias'
    headers = {'Authorization': 'Bearer ' + config['ADMIN_TOKEN']}
    record_id = None
    try:
        result = requests.get(base, params={'limite': 1}, timeout=10)
        assert result.status_code == 200
        print('GET → 200, listagem com paginação')
        result = requests.post(base, json=SAMPLES[0], headers=headers, timeout=10)
        assert result.status_code == 201
        record_id = result.json()['dados']['id']
        print(f'POST → 201, id={record_id}, Location presente')
        result = requests.put(f'{base}/{record_id}', json={**SAMPLES[0], 'status': 'resolvida'},
                              headers=headers, timeout=10)
        assert result.status_code == 200 and result.json()['dados']['status'] == 'resolvida'
        print('PUT → 200, status atualizado')
        result = requests.delete(f'{base}/{record_id}', headers=headers, timeout=10)
        assert result.status_code == 204 and not result.content
        print('DELETE → 204, corpo vazio')
        record_id = None
        result = requests.post(base, json=SAMPLES[0], timeout=10)
        assert result.status_code == 401
        print('POST sem credencial → 401')
        result = requests.get(base, params={'cidade': "' OR 1=1 --"}, timeout=10)
        assert result.status_code == 400
        print('Entrada maliciosa → 400')
    finally:
        if record_id is not None:
            requests.delete(f'{base}/{record_id}', headers=headers, timeout=10)


if __name__ == '__main__':
    main()
