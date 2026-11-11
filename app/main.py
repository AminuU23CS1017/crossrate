"""FastAPI application factory with injected provider and repository."""
import csv
import io
import os
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from .database import RateRepository
from .provider import FrankfurterProvider, ProviderError
from .service import CURRENCIES, RateService

STATIC = Path(__file__).parent / 'static'


def currency(code):
    code = code.upper()
    if code not in CURRENCIES:
        raise HTTPException(422, 'Unsupported currency. Choose one from /api/currencies.')
    return code


def create_app(database_url=None, provider=None):
    app = FastAPI(title='SP-050 Currency Exchange Rate Tracker', version='1.0.0')
    url = database_url or os.getenv('DATABASE_URL', 'sqlite:///./rates.db')
    if url.startswith('postgresql://'):
        url = url.replace('postgresql://', 'postgresql+psycopg://', 1)
    repository = RateRepository(url)
    service = RateService(provider or FrankfurterProvider(), repository)
    app.state.service = service

    @app.middleware('http')
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
            "base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
        )
        return response

    @app.exception_handler(ProviderError)
    async def provider_error(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=503, content={'detail': str(exc)})

    @app.get('/api/health')
    def health():
        return {'status': 'ok', 'project': 'SP-050'}

    @app.get('/api/currencies')
    def currencies():
        return CURRENCIES

    @app.get('/api/rates')
    def rates(base: str = 'USD', quotes: str = 'NGN,EUR,GBP,GHS'):
        base = currency(base)
        targets = sorted({currency(c.strip()) for c in quotes.split(',')})
        targets = [c for c in targets if c != base]
        if not targets or len(targets) > 11:
            raise HTTPException(422, 'Choose 1–11 target currencies different from the base.')
        return service.rates(base, targets)

    @app.get('/api/convert')
    def convert(base: str = 'USD', quote: str = 'NGN',
                amount: Decimal = Query(default=Decimal('100'), ge=0, le=Decimal('1000000000'), max_digits=18, decimal_places=8)):
        return service.convert(currency(base), currency(quote), amount)

    def history_data(base, quote, start, end):
        base, quote = currency(base), currency(quote)
        if base == quote:
            raise HTTPException(422, 'Choose different currencies for historical trends.')
        end = end or date.today()
        start = start or end - timedelta(days=30)
        if start > end or end > date.today() or (end - start).days > 366:
            raise HTTPException(422, 'Choose an ordered range of at most 366 days ending today or earlier.')
        return service.rates(base, [quote], start, end)

    @app.get('/api/history')
    def history(base: str = 'USD', quote: str = 'NGN', start: Optional[date] = None, end: Optional[date] = None):
        return history_data(base, quote, start, end)

    @app.get('/api/export')
    def export(base: str = 'USD', quote: str = 'NGN', start: Optional[date] = None, end: Optional[date] = None):
        result = history_data(base, quote, start, end)
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(['date', 'base', 'quote', 'rate', 'source', 'cache_status', 'fetched_at'])
        for row in result['rates']:
            writer.writerow([row['date'], row['base'], row['quote'], row['rate'], result['source'], result['cache_status'], result['fetched_at']])
        return Response(stream.getvalue(), media_type='text/csv', headers={
            'Content-Disposition': 'attachment; filename="exchange-rates.csv"'})

    app.mount('/static', StaticFiles(directory=STATIC), name='static')

    @app.get('/', include_in_schema=False)
    def index():
        return FileResponse(STATIC / 'index.html')

    return app
