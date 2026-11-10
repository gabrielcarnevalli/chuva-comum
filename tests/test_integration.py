"""Opt-in: usa MySQL real; remove apenas os registros criados pela própria fixture."""
import os
import threading
import socket
import json

import pytest
from mysql.connector import Error

from app import create_app
from app.audit import create_logger
from app.config import load_config
from app.db import connection
from app.repository import OccurrenceRepository
from app.tcp_service import SummaryServer, read_frame

pytestmark = [pytest.mark.integration,
              pytest.mark.skipif(os.getenv('RUN_INTEGRATION') != '1', reason='Defina RUN_INTEGRATION=1')]


@pytest.fixture
def real(tmp_path):
    config = load_config()
    config['LOG_PATH'] = str(tmp_path / 'real.log')
    repo = OccurrenceRepository(config)
    created = []
    # Registra os IDs para limpeza mesmo se um assert falhar.
    original_create = repo.create

    def tracked_create(data):
        item = original_create(data)
        created.append(item['id'])
        return item

    repo.create = tracked_create
    yield config, repo
    for record_id in created:
        repo.delete(record_id)


def test_full_crud_real_mysql(real, sample):
    config, repo = real
    app = create_app(config=config, repository=repo)
    client = app.test_client()
    headers = {'Authorization': 'Bearer ' + config['ADMIN_TOKEN']}
    created = client.post('/api/ocorrencias', json=sample, headers=headers)
    assert created.status_code == 201
    item = created.json['dados']
    record_id = item['id']
    assert item['criado_em'].endswith('Z')
    assert client.get(created.headers['Location']).json['dados'][0] == item
    # Outro repositório/conexão deve enxergar o commit.
    read = OccurrenceRepository(config).list({'id': record_id, 'pagina': 1, 'limite': 1})
    assert read[1] == 1
    for _ in range(2):
        changed = client.put(f'/api/ocorrencias/{record_id}', json={**sample, 'status': 'resolvida'}, headers=headers)
        assert changed.status_code == 200 and changed.json['dados']['status'] == 'resolvida'
    assert client.delete(f'/api/ocorrencias/{record_id}', headers=headers).status_code == 204
    assert client.get(f'/api/ocorrencias?id={record_id}').json['total'] == 0
    assert client.delete(f'/api/ocorrencias/{record_id}', headers=headers).status_code == 404


def test_sql_parameter_binding_resists_injection(real):
    _, repo = real
    # Testa diretamente a camada SQL, além da validação na API.
    items, total = repo.list({'cidade': "' OR 1=1 --", 'pagina': 1, 'limite': 100})
    assert items == [] and total == 0


def test_database_constraints_and_least_privilege(real, sample):
    config, _ = real
    with pytest.raises(Error):
        with connection(config) as conn, conn.cursor() as cursor:
            cursor.execute('INSERT INTO ocorrencias(cidade,bairro,tipo,gravidade,status) VALUES (%s,%s,%s,%s,%s)',
                           ('cidade-invalida', sample['bairro'], sample['tipo'], 'alta', 'aberta'))
    with connection(config) as conn, conn.cursor() as cursor:
        cursor.execute('SHOW GRANTS FOR CURRENT_USER()')
        grants = ' '.join(str(row) for row in cursor.fetchall()).upper()
        assert 'SELECT, INSERT, UPDATE, DELETE' in grants
        assert 'ALL PRIVILEGES' not in grants and 'CREATE' not in grants and 'DROP' not in grants


def test_transaction_rolls_back(real, sample):
    config, repo = real
    record_id = None
    with pytest.raises(RuntimeError):
        with connection(config) as conn, conn.cursor() as cursor:
            cursor.execute('INSERT INTO ocorrencias(cidade,bairro,tipo,gravidade,status) VALUES (%s,%s,%s,%s,%s)',
                           tuple(sample[key] for key in ('cidade', 'bairro', 'tipo', 'gravidade', 'status')))
            record_id = cursor.lastrowid
            raise RuntimeError('forçar rollback')
    assert repo.list({'id': record_id, 'pagina': 1, 'limite': 1})[1] == 0


def test_tcp_real_socket_segmentation_auth_and_limits(real, tmp_path):
    config, repo = real
    with SummaryServer(('127.0.0.1', 0), config['TCP_TOKEN'], repo,
                       create_logger(str(tmp_path / 'tcp.log'))) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        def send(packet, segmented=False):
            with socket.create_connection(server.server_address, timeout=4) as sock:
                if segmented:
                    for byte in packet:
                        sock.sendall(bytes([byte]))
                else:
                    sock.sendall(packet)
                return read_frame(sock)

        try:
            packet = (json.dumps({'acao': 'resumo', 'token': config['TCP_TOKEN']}) + '\n').encode()
            assert send(packet, True)['dados'] == repo.summary()
            assert 'erro' in send(b'{"acao":"resumo","token":"incorreto"}\n')
            assert 'erro' in send(b'{invalido}\n')
            assert 'erro' in send(b'x' * 1025)
            assert 'erro' in send(b'[]\n')
        finally:
            server.shutdown()
            thread.join(timeout=3)
