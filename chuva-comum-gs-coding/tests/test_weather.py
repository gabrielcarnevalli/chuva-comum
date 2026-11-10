from unittest.mock import Mock

import pytest
import requests

from app.audit import create_logger
from app.weather import WeatherService, WeatherUnavailable


@pytest.fixture
def forecast():
    return {'daily': {'time': ['2026-11-10'], 'precipitation_sum': [12.3],
                      'precipitation_probability_max': [78]},
            'daily_units': {'precipitation_sum': 'mm', 'precipitation_probability_max': '%'}}


def test_weather_json_cache_and_fixed_destination(monkeypatch, tmp_path, forecast):
    response = Mock(status_code=200)
    response.json.return_value = forecast
    get = Mock(return_value=response)
    monkeypatch.setattr('app.weather.requests.get', get)
    service = WeatherService(create_logger(str(tmp_path / 'weather.log')))
    first = service.get('sao-paulo')
    assert first['precipitacao_mm'] == 12.3 and not first['cache']
    assert service.get('sao-paulo')['cache']
    get.assert_called_once()
    assert get.call_args.args == ('https://api.open-meteo.com/v1/forecast',)
    assert get.call_args.kwargs['timeout'] == (3.05, 7)
    assert not get.call_args.kwargs['allow_redirects']


@pytest.mark.parametrize('bad_value', [None, -1, float('nan'), float('inf'), True, '20'])
def test_rejects_invalid_external_json(monkeypatch, tmp_path, forecast, bad_value):
    forecast['daily']['precipitation_sum'] = [bad_value]
    response = Mock(status_code=200)
    response.json.return_value = forecast
    monkeypatch.setattr('app.weather.requests.get', Mock(return_value=response))
    with pytest.raises(WeatherUnavailable):
        WeatherService(create_logger(str(tmp_path / 'weather.log'))).get('recife')


def test_timeout_does_not_generate_fake_forecast(monkeypatch, tmp_path):
    monkeypatch.setattr('app.weather.requests.get', Mock(side_effect=requests.Timeout()))
    service = WeatherService(create_logger(str(tmp_path / 'weather.log')))
    with pytest.raises(WeatherUnavailable):
        service.get('porto-alegre')
    assert service.cache == {}
