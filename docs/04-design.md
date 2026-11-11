# Architecture and design

## Architecture decision

Use a layered monolith: browser presentation, FastAPI HTTP endpoints, application service, provider adapter, and SQL repository. A single process is simple to develop and deploy for a student project. Dependency injection through `create_app(database_url, provider)` makes the application testable without a real network or a shared production database.

The UI and API share an origin. No CORS wildcard or browser-held provider key is required. The database contains shared provider responses, not user identities or conversion histories. Watchlists stay in localStorage on the visitor's browser. Cross-device accounts are deliberately outside scope.

```mermaid
flowchart LR
  Browser[Browser UI] -->|same-origin HTTP| API[FastAPI endpoints]
  API --> Service[RateService]
  Service --> Adapter[FrankfurterProvider]
  Service --> Repo[RateRepository]
  Adapter -->|HTTPS| External[Frankfurter API]
  Repo --> SQL[(SQLite or PostgreSQL)]
  Browser --> Local[(Browser localStorage)]
```

## UML model set

### Use cases

```mermaid
flowchart LR
  Visitor[Visitor] --> Snapshot([View reference rates])
  Visitor --> Convert([Convert amount])
  Visitor --> Trends([Explore history])
  Visitor --> Watch([Manage local watchlist])
  Visitor --> Theme([Choose theme])
  Trends --> Export([Export CSV])
  Trends --> Table([Read observation table])
  Convert --> Validate([Validate input])
  Provider[External rate provider] --> Snapshot
  Provider --> Trends
  Provider --> Convert
```

This use-case view uses Mermaid flowchart notation for compatibility. The named actors and use-case boundaries are the UML concepts; it is not a claim that Mermaid implements the full UML metamodel.

### Class diagram

```mermaid
classDiagram
  class RateProvider {
    <<interface>>
    +fetch(base, quotes, start, end)
  }
  class FrankfurterProvider {
    +fetch(base, quotes, start, end)
  }
  class RateService {
    +rates(base, quotes, start, end)
    +convert(base, quote, amount)
    +envelope(rows, fetched_at, status)
  }
  class RateRepository {
    +get(key)
    +put(key, payload, now)
  }
  class CachedResponse {
    +string key
    +string payload
    +datetime fetched_at
  }
  RateProvider <|.. FrankfurterProvider
  RateService --> RateProvider
  RateService --> RateRepository
  RateRepository --> CachedResponse
```

### Sequence: conversion

```mermaid
sequenceDiagram
  actor User
  participant UI as Browser
  participant API as FastAPI
  participant S as RateService
  participant DB as RateRepository
  participant P as Frankfurter
  User->>UI: Enter amount and pair
  UI->>API: GET /api/convert
  API->>API: Validate amount and supported codes
  API->>S: convert(base, quote, amount)
  S->>DB: get(request key)
  alt Cache younger than one hour
    DB-->>S: rows + original fetched_at
  else Missing or expired
    S->>P: Fetch daily reference rate
    alt Provider succeeds
      P-->>S: dated rows
      S->>DB: put validated rows
    else Provider unavailable
      S->>S: Use cache only if fetched within 7 days
    end
  end
  S->>S: Decimal multiplication and rounding
  S-->>API: result + source + cache status
  API-->>UI: JSON or actionable error
  UI-->>User: Display result and rate date
```

### Activity: history and export

```mermaid
flowchart TD
  Start([Start]) --> Pair[Choose pair and period]
  Pair --> Valid{Valid pair and range?}
  Valid -- No --> Error[Show validation message]
  Error --> Pair
  Valid -- Yes --> Fetch[Request cache/provider observations]
  Fetch --> Available{Observations available?}
  Available -- No --> Retry[Show unavailable state; allow retry]
  Available -- Yes --> Display[Render chart and accessible table]
  Display --> Download{Export requested?}
  Download -- Yes --> CSV[Return CSV with dates and provenance]
  Download -- No --> End([End])
  CSV --> End
```

## Database design

The data model is intentionally small: one persisted response cache. No artificial user or payment tables are included. A response is keyed by the normalized base, sorted quote codes, and optional date range. Its JSON payload stores validated observations. This avoids confusing provider observation dates with cache retrieval times.

```mermaid
erDiagram
  CACHED_RESPONSES {
    varchar key PK "Normalized request; maximum 300 characters"
    text payload "JSON array of date/base/quote/rate rows"
    timestamptz fetched_at "UTC successful fetch time"
  }
```

PostgreSQL schema is in `schema.sql`. SQLite uses the same SQLAlchemy model, with timezone normalization when values are read. `Base.metadata.create_all` is sufficient for this initial table; use a migration tool for future schema changes. Add cache cleanup and storage quotas before supporting arbitrary high-volume public queries.

## Design patterns and SOLID

**Adapter:** `FrankfurterProvider` converts upstream HTTP data into a stable internal record format and raises `ProviderError`. Changing provider need not change conversion or UI logic.

**Repository:** `RateRepository` owns SQL queries and persistence. `RateService` only calls `get` and `put`; it does not create SQL statements.

**Dependency injection:** The application factory accepts a provider and database URL. Tests inject `FakeProvider` and a temporary database.

**Single responsibility:** The service owns conversion/cache decisions, the adapter owns upstream validation, and the repository owns persistence. **Open/closed and dependency inversion:** a provider with the same `fetch` contract can be substituted without rewriting the service. The `RateProvider` Protocol documents the narrow contract. The current service accepts a repository by behavior; a formal repository Protocol could be added as the project grows.

## Wireframes

```text
DESKTOP
+------------+---------------------------------------------------+
| Crossrate  | Workspace / Overview             theme  initials  |
| Overview   +---------------------------------------------------+
| Converter  | Heading / source status / refresh                 |
| History    | [NGN rate] [EUR rate] [GBP rate] [GHS rate]         |
| Watchlist  | +----------------+ +----------------------------+ |
|            | | Amount         | | Pair / range / CSV          | |
| SP-050     | | From / To      | | Chart + exact-data table    | |
|            | | Convert/result | | Source and dates           | |
|            | +----------------+ +----------------------------+ |
|            | Watchlist / add / remove                          |
+------------+---------------------------------------------------+

MOBILE
+--------------------------------+
| Brand / icon navigation        |
| Heading / refresh / status     |
| [rate card] [rate card]         |
| [rate card] [rate card]         |
| Converter                      |
| History / chart / table / CSV  |
| Watchlist                      |
| Source / footer                |
+--------------------------------+
```

## Deployment model

Browser → HTTPS reverse proxy → Uvicorn/FastAPI → PostgreSQL and outbound HTTPS to Frankfurter. The supplied Compose setup is a local test configuration. Before public deployment: configure HTTPS, proxy request limits, database backups, retention, monitoring and dependency audits. GitHub Pages cannot execute this Python backend; do not upload only the HTML and claim the full application is hosted.
