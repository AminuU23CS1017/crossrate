# Verification and security record

## Executed automated checks — 11 November 2026

Environment: macOS, Python 3.9.6, SQLite, FastAPI 0.128.8, SQLAlchemy 2.0.57, pytest 8.4.2. Commands were run against this package, not a separate illustrative implementation.

| Check | Result |
|---|---|
| pytest | 27 passed |
| Backend statement coverage | 97.71% (171 / 175 statements) |
| Required coverage threshold | 60%; passed |
| Ruff configured checks | Passed |
| JavaScript syntax (`node --check`) | Passed |
| PostgreSQL / Docker execution | Not yet executed |
| Hosted CI / dependency audit | Configuration supplied; not yet executed |

Coverage by module: database 100%, service 100%, API 99%, provider 91%. Backend statement coverage is not frontend coverage, branch coverage, formal security assurance, or proof of production reliability.

## Test plan

Use deterministic fixture rates for arithmetic assertions. Use a temporary SQLite file for each integration test. Never depend on today's external quote as a fixed expected value.

| Area | Cases covered |
|---|---|
| Conversion | Decimal rounding, zero, same-currency identity, JPY rounding |
| Input validation | Negative, NaN, infinity, excessive amount/precision, unknown currency |
| Rate queries | Duplicate target removal, invalid code, empty targets after removing base |
| History | Reversed range, future end, oversized range, same pair, invalid date |
| Export | CSV structure, rate value, source/cache/date columns |
| Persistence | Recreate application against same database and reuse cache |
| Failure | Missing cache returns 503, allowed stale fallback, too-old fallback rejection |
| Provider adapter | Good response, missing quote, empty/malformed payload, negative/nonfinite value, future date, timeout |
| Basic integration | Page/static asset serving, health/currency endpoints, response security header |

## Manual acceptance checklist

- Confirm latest USD/NGN conversion and historical observations load from the real provider.
- Change amount and swap currencies; outdated results must be cleared while input changes.
- Add a currency to the watchlist, reload, and remove it.
- Change the trend period; inspect the exact-data table and CSV.
- Test narrow and desktop layouts, keyboard focus, and theme persistence.
- Observe explicit errors for unavailable data; do not replace a failed request with fictional rates.

The live check results are recorded in `browser-checks.md` after verification.

## Defect log

| ID | Finding | Resolution / state |
|---|---|---|
| D01 | A chart alone would hide exact observations from nonvisual users | Added semantic table and CSV; implemented |
| D02 | Responses arriving after changed inputs could show results for an old selection | Added request version counters for market, history and conversion; implemented |
| D03 | A provider outage might make old values look current | Added `fresh/cached/stale` status, original fetch times and dates; implemented |
| D04 | A backend cannot execute on GitHub Pages | Documented Python host requirement; public hosting pending |

## STRIDE threat model

| Category | Threat | Implemented control | Remaining action |
|---|---|---|---|
| Spoofing | Fake provider or substituted request destination | Fixed HTTPS upstream URL and normal TLS verification | Monitor provider/source changes |
| Tampering | Malformed rates or query injection | Allowlisted currency codes, typed dates, Decimal validation, parameterized ORM | Add more adverse-provider fixtures |
| Repudiation | Inability to trace source of downloaded data | CSV source, observation date, cache state and fetch time | Operational access logs on host |
| Information disclosure | Exposed database secret or user inputs | No browser secrets; conversion history is not persisted | Protect DB credentials in host secret store |
| Denial of service | Many uncached ranges exhaust resources | 366-day bound, curated currencies, upstream timeout/cache | Proxy rate limit, connection limits, cache size/retention |
| Elevation of privilege | Unneeded privileged account or executable input | No account mutation/admin endpoints; fixed assets; non-root Docker user | Host hardening and dependency audits |

## OWASP-oriented review

The relevant themes are broken access control (no private account resources in this release), cryptographic failures (HTTPS required in hosted mode), injection (ORM parameters and DOM text rendering), insecure design (bounded queries and explicit failure states), security misconfiguration (restrictive CSP and no broad CORS), vulnerable dependencies (audit step configured), authentication failures (accounts not implemented), integrity failures (validate upstream rows), logging/monitoring (host work pending), and SSRF (no user-controlled URL). This is a scoped review, not a penetration test or a claim of complete compliance with any OWASP edition.

## Limits

The cache TTL is measured from successful retrieval, not from the market observation date. A fresh retrieval can still contain an older official observation; the UI displays that observation date. Stale fallback lasts no more than seven days since retrieval and is explicitly identified. Rates are not refreshed continuously. Browser preferences are not backed up or synchronized. The initial DB schema uses a JSON-text cache instead of a normalized analytical warehouse.

## Version 1.1 regression checks

27 backend pytest tests passed with 97.71% statement coverage. Six Node tests passed for valid/invalid custom dates, inclusive target comparisons, stale/malformed target responses, statistics and CSV escaping/formula neutralization. `node --check app/static/app.js` and `ruff check app tests` passed. Browser evidence is in `browser-checks.md`. These checks do not claim PostgreSQL, public deployment or hosted CI validation.
