# Browser verification — 11 November 2026

Verified against the running FastAPI application at localhost, backed by a SQLite cache and the real Frankfurter API.

- The snapshot, USD/NGN conversion and 30-day chart loaded real dated observations.
- Changing the input to 200 USD produced 269,742.00 NGN at the observed reference rate of 1,348.71 on 11 November 2026. This is historical test evidence, not a promised future quote.
- The 7-day selection displayed observations dated 4–11 November 2026 and the expandable table listed matching records.
- Adding KES to the watchlist survived a page reload. Removing it worked; the default watchlist was restored after the test.
- The dark theme survived reload; light mode was restored after the test.
- Narrow-screen and 1440-pixel desktop layouts were inspected visually.
- The browser console reported no errors in the checked session.
- An inverted watchlist pair label was found and fixed: it now reads USD / NGN when the value is NGN per USD.
- Mobile icon navigation received explicit accessible names.

CSV content was verified in automated integration tests. A browser download-dialog round trip and a full assistive-technology audit were not performed. Browser QA is not a substitute for PostgreSQL or production-host testing.

## Version 1.1 follow-up

- Explicit conversion saved a recent record; clear and Undo restored it.
- Reload retained both the conversion record and a test rate target.
- A USD/NGN above-1 test target correctly reported Target met; test target removed afterwards.
- Custom dates 1–7 November 2026 returned seven dated observations with low/high/mean summaries.
- Restored the 30-day period and cleared test conversion history after verification.
- Narrow layout inspected and browser error log empty.
- Clipboard and browser CSV download interaction were not independently exercised; CSV escaping and formula-prefix neutralization are covered by Node tests.
