"""Toda entrada do cidadão é enviada como parâmetro, nunca como SQL."""
from .db import connection

COLUMNS = 'id, cidade, bairro, tipo, gravidade, status, criado_em, atualizado_em'


def serialize(row):
    return {key: value.isoformat(timespec='microseconds') + 'Z'
            if key.endswith('_em') else value for key, value in row.items()}


class OccurrenceRepository:
    def __init__(self, config):
        self.config = config

    def list(self, filters):
        # Somente nomes de colunas constantes entram na montagem do WHERE.
        conditions, values = [], []
        for key in ('cidade', 'status', 'id'):
            if key in filters:
                conditions.append(key + ' = %s')
                values.append(filters[key])
        where = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
        with connection(self.config) as conn, conn.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT COUNT(*) AS total FROM ocorrencias' + where, tuple(values))
            total = cursor.fetchone()['total']
            cursor.execute(
                f'SELECT {COLUMNS} FROM ocorrencias' + where + ' ORDER BY id DESC LIMIT %s OFFSET %s',
                tuple(values + [filters['limite'], (filters['pagina'] - 1) * filters['limite']]),
            )
            return [serialize(row) for row in cursor.fetchall()], total

    def create(self, data):
        with connection(self.config) as conn, conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                'INSERT INTO ocorrencias (cidade, bairro, tipo, gravidade, status) VALUES (%s,%s,%s,%s,%s)',
                tuple(data[key] for key in ('cidade', 'bairro', 'tipo', 'gravidade', 'status')),
            )
            cursor.execute(f'SELECT {COLUMNS} FROM ocorrencias WHERE id = %s', (cursor.lastrowid,))
            return serialize(cursor.fetchone())

    def update(self, occurrence_id, data):
        with connection(self.config) as conn, conn.cursor(dictionary=True) as cursor:
            # Bloqueio evita corrida entre consulta e alteração; PUT idêntico também retorna 200.
            cursor.execute('SELECT id FROM ocorrencias WHERE id = %s FOR UPDATE', (occurrence_id,))
            if cursor.fetchone() is None:
                return None
            cursor.execute(
                'UPDATE ocorrencias SET cidade=%s, bairro=%s, tipo=%s, gravidade=%s, status=%s WHERE id=%s',
                tuple(data[key] for key in ('cidade', 'bairro', 'tipo', 'gravidade', 'status')) + (occurrence_id,),
            )
            cursor.execute(f'SELECT {COLUMNS} FROM ocorrencias WHERE id = %s', (occurrence_id,))
            return serialize(cursor.fetchone())

    def delete(self, occurrence_id):
        with connection(self.config) as conn, conn.cursor() as cursor:
            cursor.execute('DELETE FROM ocorrencias WHERE id = %s', (occurrence_id,))
            return cursor.rowcount > 0

    def summary(self):
        with connection(self.config) as conn, conn.cursor(dictionary=True) as cursor:
            cursor.execute('SELECT status, COUNT(*) AS total FROM ocorrencias GROUP BY status')
            result = dict.fromkeys(('aberta', 'em_analise', 'resolvida'), 0)
            result.update({row['status']: row['total'] for row in cursor.fetchall()})
            return result
