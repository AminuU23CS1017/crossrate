# Software Requirements Specification — sections 1–3

## 1. Introduction

Crossrate is a read-only currency reference application for SP-050. Its purpose is to help users compare currencies and understand historical movements. It does not execute transactions. Currency amounts are computed from provider observations using Decimal arithmetic. Values are reference estimates, not executable quotes.

## 2. Overall description

The browser talks to one FastAPI server. The server validates requests, queries a cache repository, and calls Frankfurter when appropriate. A SQL database persists response payloads and fetch timestamps. The browser stores watchlist codes, appearance preference, up to 10 rate targets and the latest 20 explicitly requested conversions locally. These personal records are not persisted on the server. Assumed users have a modern browser and access to the running server. The first request for an uncached pair requires internet access from the server.

Stakeholder requirements below are proposed, based on the assignment and intended use. They require validation with the lecturer and actual users. No interviews or surveys are claimed.

## 3. Specific requirements

| ID | Priority | Functional requirement | Acceptance criterion |
|---|---|---|---|
| FR01 | Must | List supported currencies | `/api/currencies` returns the 12 documented codes and labels. |
| FR02 | Must | Display latest pair rates | Snapshot values identify base, quote and observation date. |
| FR03 | Must | Convert a valid amount | `2 × 1500.125` produces `3000.25` using the deterministic fixture. |
| FR04 | Must | Reject invalid inputs | Negative, nonfinite and over-limit amounts and unknown codes return 422. |
| FR05 | Should | Swap conversion currencies | Swap exchanges the selected codes and recalculates. |
| FR06 | Must | Show historical observations | An ordered range of at most 366 days returns dated rows and a chart. |
| FR07 | Must | Provide accessible history | All chart observations are available in an expandable HTML table. |
| FR08 | Must | Export CSV | Export includes dates, pair, rate, source, cache status and fetch timestamp. |
| FR09 | Should | Maintain a watchlist | Add/remove codes; changes survive reload in the same browser. |
| FR10 | Must | Handle provider failure | Return 503 with no valid cached response; otherwise label allowed fallback as stale. |
| FR11 | Must | Persist cache | A second app instance using the same DB can reuse a valid saved response. |
| FR12 | Should | Remember appearance | Theme choice survives browser reload when storage is available. |
| FR13 | Must | Identify data provenance | Results show source, observation date and fetch time where applicable. |
| FR14 | Should | Handle identical currencies | Return rate 1 without provider calls; use no fabricated market date. |
| FR15 | Should | Choose custom historical dates | Reject invalid, reversed, future and over-366-day ranges. |
| FR16 | Should | Summarize observations | Show low, high and arithmetic mean of returned observations. |
| FR17 | Should | Save reference-rate targets | Persist up to 10 above/below targets locally; inclusive threshold checks; stale data cannot mark a target met. |
| FR18 | Should | Reuse conversion history | Persist latest 20 explicit conversions, reuse inputs, export CSV and clear with Undo. |
| FR19 | Should | Copy a conversion | Copy result with source, date and cache status; disable copying after inputs change. |

| ID | Non-functional requirement | Verification target |
|---|---|---|
| NFR01 | Accuracy | Use Decimal and round half-up; 2 decimal result places except JPY (0). |
| NFR02 | Resilience | 12-second upstream timeout; one-hour cache TTL; stale fallback at most 7 days since fetch. |
| NFR03 | Accessibility | Keyboard controls, visible focus, labels, live statuses, chart table and reduced-motion support. Manual review, not a formal WCAG certification. |
| NFR04 | Security | Fixed upstream URL, allowlisted currencies, validated bounded requests, no secret in browser code, parameterized SQLAlchemy operations. |
| NFR05 | Maintainability | Provider Adapter and Repository abstractions; independently testable service. |
| NFR06 | Testability | At least 60% backend statement coverage and tests for key error paths. |
| NFR07 | Performance | Cached API request target below 1 second on a developer machine; measure under a defined load before claiming production capacity. |
| NFR08 | Portability | Run with SQLite locally; supply PostgreSQL configuration. Validate PostgreSQL before a deployment claim. |

### User stories

| ID | Story | Given / When / Then |
|---|---|---|
| US01 | As a traveller, I want to convert an amount. | Given a supported pair, when I enter a valid amount and convert, then the estimate and rate date are displayed. |
| US02 | As a student, I want to compare key currencies. | Given a selected base, when the snapshot loads, then each card shows quote units per one base unit. |
| US03 | As a returning user, I want my saved currencies. | Given a saved watchlist, when I reload, then the same codes are loaded from this browser. |
| US04 | As a researcher, I want historical trends. | Given different currencies, when I choose 30 days, then dated observations appear on a chart and table. |
| US05 | As a keyboard user, I want the chart data without a mouse. | Given the history panel, when I tab to and expand the table, then all observations are readable. |
| US06 | As a spreadsheet user, I want exported data. | Given a successful history request, when I export, then CSV contains the selected pair and observation dates. |
| US07 | As a user, I want honest failure messages. | Given an upstream failure, when I request rates, then cached data is marked stale or an unavailable message is shown. |
| US08 | As a night-time user, I want a dark interface. | Given the theme control, when I toggle it and reload, then my choice persists. |
| US09 | As a user, I want input mistakes caught. | Given a negative amount, when conversion is attempted, then it is rejected without a misleading result. |

### Validation and traceability

Review these requirements with the lecturer before freezing scope. Tests in `tests/test_app.py` exercise FR01–04, FR06, FR08, FR10–11 and FR14. Browser review covers FR05, FR07, FR09 and FR12. FR13 appears in provider envelopes, CSV, cards and result panels. Visual/manual evidence and current limitations are recorded in the verification document.
