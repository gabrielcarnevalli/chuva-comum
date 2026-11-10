"""Consome somente Open-Meteo em HTTPS; sem URL controlada pelo cliente."""
import math
import threading
import time
from datetime import date, datetime, timezone

import requests

from .audit import audit
from .validation import CITIES

URL = 'https://api.open-meteo.com/v1/forecast'


class WeatherUnavailable(Exception):
    pass


class WeatherService:
    def __init__(self, logger):
        self.logger = logger
        self.cache = {}
        self.lock = threading.Lock()

    def get(self, city):
        with self.lock:
            cached = self.cache.get(city)
            if cached and time.monotonic() - cached[0] < 600:
                return {**cached[1], 'cache': True}
            try:
                # O timeout de conexão/leitura impede espera indefinida por rede.
                response = requests.get(URL, params={
                    'latitude': CITIES[city]['latitude'], 'longitude': CITIES[city]['longitude'],
                    'daily': 'precipitation_sum,precipitation_probability_max',
                    'forecast_days': 1, 'timezone': 'America/Sao_Paulo',
                }, timeout=(3.05, 7), allow_redirects=False)
                response.raise_for_status()
                if response.status_code != 200:
                    raise ValueError('Status inesperado')
                data = response.json()
                daily, units = data['daily'], data['daily_units']
                mm = daily['precipitation_sum'][0]
                probability = daily['precipitation_probability_max'][0]
                day = daily['time'][0]
                date.fromisoformat(day)
                if (isinstance(mm, bool) or not isinstance(mm, (int, float)) or not math.isfinite(mm)
                        or not 0 <= mm <= 3000 or isinstance(probability, bool)
                        or not isinstance(probability, (int, float)) or not 0 <= probability <= 100
                        or units['precipitation_sum'] != 'mm'
                        or units['precipitation_probability_max'] != '%'):
                    raise ValueError('Dados externos inválidos')
                result = {
                    'cidade': city, 'data': day, 'precipitacao_mm': mm,
                    'probabilidade_chuva': probability, 'fonte': 'Open-Meteo',
                    'consultado_em': datetime.now(timezone.utc).isoformat(), 'cache': False,
                    'aviso': 'Previsão municipal. Não prevê alagamentos nem substitui alertas oficiais.',
                }
                self.cache[city] = (time.monotonic(), result)
                audit(self.logger, 'clima.consultar', 'sucesso', cidade=city)
                return result
            except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
                audit(self.logger, 'clima.consultar', 'indisponivel', cidade=city)
                # Sem fallback fictício apresentado como previsão atual.
                raise WeatherUnavailable() from None
