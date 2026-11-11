# Crossrate — SP-050 Currency Exchange Rate Tracker

A working Software Engineering project for Aminu Ibrahim Ayomide, final-year Computer Science student at the Air Force Institute of Technology.

**Project ID:** SP-050 · **Domain:** Finance & Fintech · **Level:** Intermediate

## What works

**Version 1.1:** custom historical dates, daily reference-rate targets, saved conversion history with reuse/undo/CSV, copyable results, and low/high/mean trend summaries. Targets and history are browser-local. Targets are evaluated on page load, Refresh data, or Check now; there is no background monitoring.

- Daily reference rates for 12 supported currencies, including NGN, USD, EUR, GBP, GHS and KES.
- Decimal-based conversion, currency swapping, and input validation.
- Historical line charts, an accessible observation table, and CSV download.
- Browser-local watchlists and remembered light/dark appearance.
- SQLAlchemy persistence with a one-hour response cache and clearly labeled fallback data.
- A FastAPI backend with PostgreSQL support and a zero-setup SQLite default.
- Automated tests, CI configuration, Docker configuration, and coursework documentation.

Rates are sourced from Frankfurter. They are daily blended reference values, not live tradable prices, bank quotes, or guaranteed remittance rates. Weekends and other non-publication dates may be absent. Each observation keeps its actual date. No account, payment, trading, or email functionality is included.

## Run locally

Use Python 3.9 or later. Python 3.12 is recommended for a new installation.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:create_app --factory --reload --host 127.0.0.1 --port 8000
```

Windows activation: `.venv\Scripts\activate`.

Open **http://127.0.0.1:8000**. The SQLite cache is created as `rates.db` in the current directory. An internet connection is needed for first-time currency requests. Cached matching requests remain available under the documented fallback policy.

Optional frontend logic tests (Node.js 18+): `node --test tests/features.test.cjs`.

Run from this project directory. The app reads `DATABASE_URL` from the environment; it does not automatically read `.env`.

## PostgreSQL

```sh
export DATABASE_URL='postgresql+psycopg://tracker:YOUR_PASSWORD@localhost:5432/tracker'
python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

Create the user and database first. Tables are created on startup. Alternatively, install Docker, set `POSTGRES_PASSWORD` to a strong URL-safe value, and run `docker compose up --build`. The included Compose file binds the app to localhost and persists PostgreSQL data in a named volume. PostgreSQL/Docker are supplied configurations; the verified local run used SQLite.

## Verify

```sh
python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=60
ruff check app tests
```

Recorded verification: 27 tests passed, 97.71% backend statement coverage, and Ruff passed. The tests use deterministic provider fixtures; they do not treat fluctuating live rates as fixed expected values. See [verification](docs/05-verification.md) for scope and limits.

## Project documentation

1. [Proposal and process model](docs/01-proposal.md)
2. [Requirements and acceptance criteria](docs/02-requirements.md)
3. [Backlog, 13-week plan and risks](docs/03-plan.md)
4. [Architecture, UML, database and patterns](docs/04-design.md)
5. [Testing, security and evidence](docs/05-verification.md)
6. [User manual, technical guide and submission checklist](docs/06-handbook.md)

The workbook is a course brief, not evidence of completed coursework. Peer review, lecturer feedback, personal reflection, remote repository publication, hosted deployment, and PostgreSQL validation remain explicitly pending. Do not submit them as completed activities.

## API

| Endpoint | Purpose |
|---|---|
| `GET /api/currencies` | Supported currency codes and names |
| `GET /api/rates?base=USD&quotes=NGN,EUR` | Latest rates |
| `GET /api/convert?base=USD&quote=NGN&amount=100` | Decimal conversion |
| `GET /api/history?base=USD&quote=NGN&start=2026-01-01&end=2026-01-31` | Historical observations |
| `GET /api/export` | Same pair/date arguments as history, returned as CSV |
| `GET /api/health` | Application liveness, not provider availability |

Interactive API schema: `/docs`. The application CSP is deliberately restrictive; use `/openapi.json` if the externally loaded Swagger interface is blocked. The main application requires no CDN scripts or fonts.

## Source

Assignment: `SE_Personal_Projects_13_Weeks.xlsx`, Project Topics row 51; Weekly Tasks rows 639–651; 13-Week Plan rows 2–14. Data/API documentation: https://frankfurter.dev/ (consulted 11 November 2026).
