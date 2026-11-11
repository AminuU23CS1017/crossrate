from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.provider import FrankfurterProvider, ProviderError


class FakeProvider:
    def __init__(self):
        self.calls = 0
        self.fail = False

    def fetch(self, base, quotes, start=None, end=None):
        self.calls += 1
        if self.fail:
            raise ProviderError('Provider unavailable')
        dates = [start, end] if start else [date.today()]
        return [{'base': base, 'quote': q, 'date': d.isoformat(), 'rate': '1500.125'} for d in dates for q in quotes]


@pytest.fixture
def setup(tmp_path):
    provider = FakeProvider()
    app = create_app('sqlite:///' + str(tmp_path / 'test.db'), provider)
    with TestClient(app) as client:
        yield client, app.state.service, provider


def test_health_and_page(setup):
    client, _, _ = setup
    assert client.get('/api/health').json()['project'] == 'SP-050'
    page = client.get('/')
    assert page.status_code == 200 and 'crossrate' in page.text
    assert page.headers['X-Frame-Options'] == 'DENY'
    assert client.get('/static/app.js').status_code == 200
    assert 'NGN' in client.get('/api/currencies').json()


def test_conversion_and_cache(setup):
    client, _, provider = setup
    result = client.get('/api/convert', params={'amount': '2', 'base': 'usd', 'quote': 'ngn'}).json()
    assert result['converted'] == '3000.25' and result['cache_status'] == 'fresh'
    assert client.get('/api/convert').json()['cache_status'] == 'cached'
    assert provider.calls == 1


def test_zero_and_identity(setup):
    client, _, provider = setup
    assert client.get('/api/convert', params={'amount': 0}).json()['converted'] == '0.00'
    identity = client.get('/api/convert', params={'base': 'JPY', 'quote': 'JPY', 'amount': '3.5'}).json()
    assert identity['converted'] == '4' and identity['date'] is None
    assert provider.calls == 1


@pytest.mark.parametrize('params', [{'amount': '-1'}, {'amount': 'NaN'}, {'amount': 'Infinity'}, {'amount': '1000000001'}, {'base': 'XXX'}, {'quote': '<script>'}, {'amount': '.123456789'}])
def test_invalid_conversion(setup, params):
    assert setup[0].get('/api/convert', params=params).status_code == 422


def test_market_validation(setup):
    client, _, _ = setup
    assert client.get('/api/rates', params={'base': 'USD', 'quotes': 'USD'}).status_code == 422
    assert client.get('/api/rates', params={'quotes': 'ABC'}).status_code == 422
    assert client.get('/api/rates', params={'quotes': 'NGN,EUR,NGN'}).status_code == 200


@pytest.mark.parametrize('params', [{'base': 'USD', 'quote': 'USD'}, {'start': '2025-02-01', 'end': '2025-01-01'}, {'start': '2020-01-01', 'end': '2022-01-01'}, {'end': '2999-01-01'}, {'start': 'not-a-date'}])
def test_history_validation(setup, params):
    assert setup[0].get('/api/history', params=params).status_code == 422


def test_history_and_csv(setup):
    client, _, _ = setup
    assert len(client.get('/api/history').json()['rates']) == 2
    export = client.get('/api/export')
    assert export.status_code == 200 and 'text/csv' in export.headers['content-type']
    assert 'date,base,quote,rate,source,cache_status,fetched_at' in export.text
    assert '1500.125' in export.text


def test_failure_and_stale_fallback(setup):
    client, service, provider = setup
    provider.fail = True
    assert client.get('/api/convert').status_code == 503
    provider.fail = False
    result = service.rates('USD', ['NGN'])
    key = 'USD|NGN|None|None'
    service.repository.put(key, result['rates'], datetime.now(timezone.utc) - timedelta(hours=2))
    provider.fail = True
    stale = service.rates('USD', ['NGN'])
    assert stale['cache_status'] == 'stale' and stale['warning']
    service.repository.put(key, result['rates'], datetime.now(timezone.utc) - timedelta(days=8))
    with pytest.raises(ProviderError):
        service.rates('USD', ['NGN'])


def test_persistence(tmp_path):
    url = 'sqlite:///' + str(tmp_path / 'rates.db')
    create_app(url, FakeProvider()).state.service.convert('USD', 'NGN', Decimal('1'))
    provider = FakeProvider()
    service = create_app(url, provider).state.service
    assert service.convert('USD', 'NGN', Decimal('1'))['cache_status'] == 'cached'
    assert provider.calls == 0


def test_adapter(monkeypatch):
    payload = [{'date': date.today().isoformat(), 'base': 'USD', 'quote': 'NGN', 'rate': 1500}]
    monkeypatch.setattr(httpx, 'get', lambda *a, **k: httpx.Response(200, json=payload, request=httpx.Request('GET', 'https://example.test')))
    assert FrankfurterProvider().fetch('USD', ['NGN'])[0]['rate'] == '1500'
    with pytest.raises(ProviderError):
        FrankfurterProvider().fetch('USD', ['EUR'])


@pytest.mark.parametrize('payload', [[], {}, [{'rate': -1, 'date': '2025-01-01', 'base': 'USD', 'quote': 'NGN'}], [{'rate': 'NaN', 'date': '2025-01-01', 'base': 'USD', 'quote': 'NGN'}], [{'rate': 1, 'date': '2999-01-01', 'base': 'USD', 'quote': 'NGN'}], [{'broken': True}]])
def test_adapter_rejects_bad_data(monkeypatch, payload):
    monkeypatch.setattr(httpx, 'get', lambda *a, **k: httpx.Response(200, json=payload, request=httpx.Request('GET', 'https://example.test')))
    with pytest.raises(ProviderError):
        FrankfurterProvider().fetch('USD', ['NGN'])


def test_timeout(monkeypatch):
    def fail(*args, **kwargs):
        raise httpx.ReadTimeout('timeout')
    monkeypatch.setattr(httpx, 'get', fail)
    with pytest.raises(ProviderError):
        FrankfurterProvider().fetch('USD', ['NGN'])
