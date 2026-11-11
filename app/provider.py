"""Adapter isolates the external API from application logic."""
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Protocol

import httpx


class ProviderError(Exception):
    pass


class RateProvider(Protocol):
    def fetch(self, base, quotes, start=None, end=None): ...


class FrankfurterProvider:
    URL = 'https://api.frankfurter.dev/v2/rates'

    def fetch(self, base, quotes, start=None, end=None):
        params = {'base': base, 'quotes': ','.join(quotes)}
        if start:
            params.update({'from': start.isoformat(), 'to': end.isoformat()})
        try:
            response = httpx.get(self.URL, params=params, timeout=12)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list) or not data:
                raise ValueError('No rates returned')
            rows = []
            for row in data:
                value = Decimal(str(row['rate']))
                day = date.fromisoformat(row['date'])
                if (not value.is_finite() or value <= 0 or row['base'] != base
                        or row['quote'] not in quotes or day > date.today()):
                    raise ValueError('Invalid provider record')
                if start and not start <= day <= end:
                    raise ValueError('Rate outside requested period')
                rows.append({'date': day.isoformat(), 'base': base,
                             'quote': row['quote'], 'rate': str(value)})
            # Never silently drop an unavailable target currency.
            if set(quotes) != {row['quote'] for row in rows}:
                raise ValueError('Incomplete currency coverage')
            return sorted(rows, key=lambda row: (row['date'], row['quote']))
        except (httpx.HTTPError, ValueError, KeyError, TypeError, InvalidOperation) as exc:
            raise ProviderError('Rate provider is temporarily unavailable for this request.') from exc
