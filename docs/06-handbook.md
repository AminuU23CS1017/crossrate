# User manual and technical handover

## Using Crossrate

1. Start the server using the README commands and open its localhost address.
2. Choose a market base. Each snapshot card shows quote-currency units for one base unit, plus its reference date.
3. In the converter, enter a nonnegative amount, choose From and To, and select Convert. Use the swap control to reverse the pair. Fees and bank spreads are excluded.
4. In Historical trends, select two different currencies and a period. Read the movement percentage as change from the first returned observation to the last returned observation; it is not a prediction.
5. Expand the accessible table for exact observations. Export CSV downloads those dates, pair values, and provenance columns.
6. Add/remove watchlist currencies. The numbers use the market base selected above. Preferences stay only in this browser.
7. Select the theme button to switch light/dark mode.

## Data states and troubleshooting

- **Fresh:** just fetched successfully. The rate date may precede today.
- **Cached:** fetched within the past hour. Refresh reloads application data but does not bypass the server's cache TTL.
- **Stale:** a provider request failed and a matching saved response, fetched no more than seven days ago, was available. See the explicit warning and dates.
- **Unavailable:** no acceptable matching data exists. Retry later or use another supported pair/period.
- Empty watchlist is valid. If storage is disabled, the page explains that changes will not persist.
- If page styling or requests fail, run from the project directory and visit the server URL, not the HTML file directly.
- If port 8000 is in use, start Uvicorn with another port and open that address.

## Maintenance

Provider parsing lives in `app/provider.py`. Business rules and decimal rounding live in `app/service.py`. Database access lives in `app/database.py`. Routes and validation live in `app/main.py`. Browser files are under `app/static/`. Add tests before changing assumptions, and update requirements and diagrams when the scope changes.

To add a currency, verify provider coverage and currency precision before updating `CURRENCIES` and rounding rules. The current curated list uses two decimal places except JPY. Do not generalize that rule to every currency without validating minor-unit conventions.

Before hosting, run PostgreSQL tests, run the dependency audit, configure HTTPS/proxy limits, set environment secrets and persistent storage, and document an actual deployment URL. No public deployment is claimed by this package. Keep `.env`, databases and cached user artifacts out of Git.

## Suggested demo script (5–7 minutes)

- Explain the problem, target users and scope in one minute.
- Show a USD/NGN conversion and its source date.
- Swap currencies and show invalid-input handling.
- Change the trend period, open the exact-data table, and export CSV.
- Add a watchlist currency and reload to demonstrate persistence.
- Explain Adapter/Repository and the cache failure policy.
- Show the real test output and identify remaining hosting/peer-review work.

## Report and reflection prompts

Use the prepared proposal, SRS, plan, design and verification documents as the technical foundation of your report. Add your own screenshots, feedback and explanations. Complete these items yourself after genuine activities:

- What did you learn about external API dependencies and reference-rate dates?
- Which design choice changed after feedback, and why?
- Which defect was hardest for you to understand and fix?
- What tradeoff did you make between simplicity and future features?
- Who reviewed the project, what did they actually report, and how did you respond?
- What remains incomplete, and what would your next iteration address?

Do not invent peer names, review dates, interviews, sprint history, or marks. A reflection should describe your own understanding and experience.

## Submission checklist

- [x] Working application source and reproducible local setup
- [x] Proposal and incremental process rationale
- [x] Requirements, acceptance criteria and user stories
- [x] Prioritized plan and risk register
- [x] UML-style diagrams, schema, pattern and SOLID discussion
- [x] Automated tests and recorded coverage
- [x] CI and Docker configuration
- [x] User and technical documentation
- [ ] Student matriculation number/course details
- [ ] Lecturer validation and real user feedback
- [ ] Genuine peer review and personal reflection
- [ ] Remote repository and pull-request evidence
- [ ] PostgreSQL, hosted CI, dependency-audit and deployment evidence
- [ ] Final presentation and assessment

## Version 1.1 features

- **Custom dates:** Select Custom dates under Historical trends, enter start/end, then Apply. The inclusive range must be at most 366 days and cannot end in the future. Low, high and mean summarize returned observations, not every calendar day.
- **Rate alerts:** Choose two different currencies, Above or Below, and a positive threshold. Save up to 10 targets. Above means greater than or equal; Below means less than or equal. Checks run on load, Refresh data and Check now. These are cached reference-rate checks, not background monitoring or email notifications. Stale fallback data is marked unavailable for target evaluation.
- **Recent conversions:** Explicit Convert, swap and Use again actions save the latest 20 results in this browser. Use again recalculates at the currently available rate. Export history downloads CSV with provenance. Clear history offers Undo until reload; export first if a durable backup is needed.
- **Copy result:** Copies the estimate, rate, date, source and cache status. If clipboard access is unavailable, select the result text manually.
- **Privacy:** Targets and recent conversions live in localStorage on this browser/device; clearing site data removes them. They are not account-synced. API requests still send the selected amount/pair to your running application as needed for conversion.
