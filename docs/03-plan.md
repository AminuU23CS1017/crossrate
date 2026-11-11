# Delivery plan and risk register

## Prioritized backlog and estimates

These are planning estimates for a student implementing and understanding the work, not a claim of time already spent.

| Item | Priority | Estimate (hours) | Current state |
|---|---|---:|---|
| Proposal and scope validation | Must | 4 | Draft prepared; lecturer validation pending |
| Requirements and acceptance criteria | Must | 6 | Draft prepared |
| UML, architecture and schema | Must | 8 | Prepared |
| Provider integration and cache | Must | 10 | Implemented; SQLite verified |
| Converter and validation | Must | 8 | Implemented and tested |
| Historical chart and table | Must | 8 | Implemented |
| CSV export | Must | 3 | Implemented and tested |
| Watchlist and theme | Should | 4 | Implemented |
| Automated tests and quality checks | Must | 8 | Executed |
| Security review and CI | Must | 6 | Review/configuration prepared; hosted execution pending |
| PostgreSQL and deployment validation | Must | 6 | Pending environment setup |
| Manual, final report, demonstration and reflection | Must | 9 | Manual prepared; personal assessment tasks pending |
| **Total planned effort** | | **80** | |

Implemented in v1.1: chosen historical dates, browser-local rate targets and conversion history. Could-have: additional currency coverage. Won't-have in this release: trading, money transfers, shared accounts and live tick data.

## 13-week mapping

| Week | Assignment focus / marks | Evidence in this package | Remaining activity |
|---|---|---|---|
| 1 | Proposal and process / 4 | `01-proposal.md`, README, local source | Publish a remote Git repository and record its URL |
| 2 | Requirements / 8 | `02-requirements.md` (19 FR, 8 NFR, 9 stories) | Validate with stakeholders |
| 3 | Planning / 6 | This backlog, estimates, schedule and risks | Align with actual academic dates |
| 4 | UML / 8 | Use case, class, sequence and activity models in `04-design.md` | Review notation with lecturer |
| 5 | Architecture/database / 8 | Component model, data model, PostgreSQL schema | Test PostgreSQL |
| 6 | Patterns/UI / 6 | Adapter/Repository notes, SOLID, wireframes | Collect usability feedback |
| 7 | Core implementation / 6 | Converter, cache, provider and backend source | Use a remote feature branch/PR for the next change |
| 8 | Prototype review / 10 | Runnable core flow | Present demo; record actual feedback |
| 9 | Remaining modules / 6 | Chart, watchlist, export; Ruff result | Obtain genuine peer review |
| 10 | Testing / 8 | 27 backend and 6 frontend tests; recorded coverage | Extend system testing with users |
| 11 | Security/DevOps / 8 | Threat model, CI, Docker files | Run CI remotely and deploy to test host |
| 12 | Maintenance/docs / 6 | Manual, change record, metrics | Track an actual external change request if required |
| 13 | Final assessment / 16 | Demo script and final-report outline | Student presentation, reflection, peer assessment |

Total marks: 100. The package does not claim 13 weeks of work or completed assessment.

## Risk register

| Risk | Likelihood / impact | Mitigation | Trigger / response |
|---|---|---|---|
| Provider outage or limit | Medium / high | Timeout, cache, explicit status | 503: retry later; do not invent rates |
| Misreading reference values as trade quotes | Medium / high | Visible reference-rate and fee labels | Keep dates and source next to outputs |
| No observations for requested range | Medium / medium | Clear errors; change pair or period | Do not interpolate missing days |
| Poor connectivity | Medium / medium | Cache successful queries | Show cached/stale state and original dates |
| Browser storage disabled | Low / low | In-memory fallback with notice | Explain preference cannot persist |
| Public API abuse | Medium / high for hosting | Allowlist and range bounds | Add proxy rate limiting before public rollout |
| PostgreSQL setup mismatch | Medium / medium | Explicit driver and Compose file | Run integration tests with target DB |
| Academic scope grows | Medium / high | MoSCoW and incremental reviews | Log impact before accepting additions |

## Change record CR-001

**Issue:** A chart alone excludes readers who need exact observations or keyboard-accessible data.  
**Change:** Include an expandable observation table and CSV provenance columns.  
**Impact:** Frontend table rendering and CSV schema; no additional provider requests; one extra system acceptance criterion.  
**State:** Implemented in this initial package and covered by CSV tests. This is a documented design improvement, not a fabricated external stakeholder request.

## Change record CR-002 — version 1.1

**Request:** Improve the application and add more features.  
**Change:** Custom dates, trend statistics, browser-local rate targets, recent conversions with reuse/export/clear/Undo, copy with provenance, and active navigation.  
**Impact:** Frontend features and six Node tests; no database migration or new backend endpoint. Targets use existing cached reference-rate endpoints, checked on page load and manual refresh/check. There are no background or email notifications.  
**Verification:** 27 backend tests and six frontend tests passed; persistence, custom ranges, target detection and Undo checked in the browser. PostgreSQL and public hosting remain unverified.
