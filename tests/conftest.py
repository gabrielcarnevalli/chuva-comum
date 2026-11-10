from unittest.mock import Mock

import pytest

from app import create_app


@pytest.fixture
def sample():
    return {'cidade': 'sao-paulo', 'bairro': 'Setor Norte', 'tipo': 'alagamento',
            'gravidade': 'alta', 'status': 'aberta'}


@pytest.fixture
def app(tmp_path, sample):
    repo = Mock()
    item = {**sample, 'id': 7, 'criado_em': '2026-01-01T10:00:00Z',
            'atualizado_em': '2026-01-01T10:00:00Z'}
    repo.create.return_value = item
    repo.update.return_value = item
    repo.list.return_value = ([], 0)
    repo.delete.return_value = True
    config = {'TESTING': True, 'ADMIN_TOKEN': 'a' * 48, 'TCP_TOKEN': 'b' * 48,
              'LOG_PATH': str(tmp_path / 'audit.log'), 'MAX_CONTENT_LENGTH': 4096}
    return create_app(config=config, repository=repo, weather=Mock())


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def headers():
    return {'Authorization': 'Bearer ' + 'a' * 48}
