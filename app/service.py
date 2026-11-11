"""Business rules and caching, independent of HTTP and database details."""
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from .provider import ProviderError

CURRENCIES = {
    'USD': 'US Dollar', 'NGN': 'Nigerian Naira', 'EUR': 'Euro',
    'GBP': 'British Pound', 'GHS': 'Ghanaian Cedi', 'KES': 'Kenyan Shilling',
    'ZAR': 'South African Rand', 'CAD': 'Canadian Dollar', 'AUD': 'Australian Dollar',
    'JPY': 'Japanese Yen', 'CHF': 'Swiss Franc', 'CNY': 'Chinese Yuan',
}


class RateService:
    TTL_SECONDS = 3600
    MAX_FALLBACK_SECONDS = 7 * 86400

    def __init__(self, provider, repository):
        self.provider = provider
        self.repository = repository

    def rates(self, base, quotes, start=None, end=None):
        now = datetime.now(timezone.utc)
        key = '|'.join([base, ','.join(sorted(quotes)), str(start), str(end)])
        cached = self.repository.get(key)
        if cached and (now - cached[1]).total_seconds() < self.TTL_SECONDS:
            return self.envelope(cached[0], cached[1], 'cached')
        try:
            rows = self.provider.fetch(base, quotes, start, end)
        except ProviderError:
            if cached and (now - cached[1]).total_seconds() <= self.MAX_FALLBACK_SECONDS:
                return self.envelope(cached[0], cached[1], 'stale')
            raise
        self.repository.put(key, rows, now)
        return self.envelope(rows, now, 'fresh')

    @staticmethod
    def envelope(rows, fetched_at, status):
        return {'rates': rows, 'source': 'Frankfurter blended reference rates',
                'source_url': 'https://frankfurter.dev/',
                'fetched_at': fetched_at.isoformat(), 'cache_status': status,
                'warning': 'Provider unavailable. Showing previously saved data.' if status == 'stale' else None}

    def convert(self, base, quote, amount):
        if base == quote:
            return {'amount': str(amount), 'converted': str(amount.quantize(Decimal('1') if quote == 'JPY' else Decimal('.01'), rounding=ROUND_HALF_UP)),
                    'rate': '1', 'base': base, 'quote': quote, 'date': None,
                    'source': 'Identity conversion; no external rate used', 'cache_status': 'identity'}
        result = self.rates(base, [quote])
        row = result['rates'][-1]
        converted = (amount * Decimal(row['rate'])).quantize(
            Decimal('1') if quote == 'JPY' else Decimal('.01'), rounding=ROUND_HALF_UP)
        return {**result, **row, 'amount': str(amount), 'converted': str(converted)}
