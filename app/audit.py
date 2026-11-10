"""Auditoria sem corpo, IP, cabeçalhos ou credenciais; datas em UTC."""
import json
import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path


def create_logger(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    logger = logging.Logger('chuva.audit')
    handler = RotatingFileHandler(path, maxBytes=1_000_000, backupCount=3, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)sZ %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
    formatter.converter = time.gmtime
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def audit(logger, action, result, **metadata):
    logger.info(json.dumps({'acao': action, 'resultado': result, **metadata}, ensure_ascii=False))
