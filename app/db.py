"""Conexões curtas e transações com rollback automático; sem ORM."""
from contextlib import contextmanager

import mysql.connector


@contextmanager
def connection(config):
    conn = mysql.connector.connect(
        host=config['DB_HOST'], port=config['DB_PORT'], database=config['DB_NAME'],
        user=config['DB_USER'], password=config['DB_PASSWORD'], connection_timeout=5,
        charset='utf8mb4', time_zone='+00:00', autocommit=False,
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
