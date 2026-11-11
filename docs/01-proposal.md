# Project proposal

**Title:** Currency Exchange Rate Tracker (Crossrate)  
**Project:** SP-050  
**Student:** Aminu Ibrahim Ayomide  
**Institution:** Air Force Institute of Technology  
**Matriculation number:** To be supplied  
**Course / lecturer:** To be supplied

## Problem

People comparing amounts across currencies often switch between multiple sources without a clear indication of the rate date, source, or whether a quoted amount includes fees. Students and travellers also need a simple way to review how a currency pair has changed over a chosen period. Copying rates manually into calculations introduces avoidable mistakes.

## Proposed solution

Develop a responsive web application that displays daily reference exchange rates, converts a user-entered amount, charts historical observations, and lets visitors maintain a watchlist. Every external result identifies its source and observation date. Users can download the historical observations as CSV for further analysis.

## Target users and stakeholders

Primary users are students, travellers, and people making informal cross-currency comparisons. The student developer maintains the software. The lecturer evaluates engineering deliverables. Frankfurter supplies the external data. Hosting and database operators become stakeholders when a hosted environment is selected. These are proposed personas; no stakeholder interviews have yet been conducted.

## Objectives

1. Convert valid amounts accurately using decimal arithmetic and a dated external rate.
2. Provide current reference values and up to one year of historical observations for supported pairs.
3. Keep the application useful during short provider outages using labeled cached responses.
4. Deliver a responsive and keyboard-operable interface with an accessible alternative to the chart.
5. Demonstrate requirements engineering, modular design, automated testing, and reproducible setup.

## Scope

The first release supports 12 curated currencies, conversion, 7/30/90/365-day trends, CSV export, browser-local watchlists, and themes. The backend exposes read-only endpoints and persists response caches. PostgreSQL is the suggested deployment database; SQLite is provided for accessible local development.

Payments, cryptocurrency trading, investment advice, bank spreads, account registration, cross-device synchronization, email alerts, and intraday ticks are outside this release. Browser-local watchlists are not user accounts.

## Process model: incremental development

Use an incremental model with a short review at the end of each weekly activity. Each increment should produce something testable: requirements and initial UI, conversion and cache, historical chart/export, then hardening and documentation. This fits a single-student, 13-week project and makes third-party API assumptions visible early. Full Scrum roles and ceremonies would add overhead for one developer. A strict Waterfall approach would delay feedback on the provider integration and interface.

## Success criteria

The converter, chart, watchlist and export must meet their acceptance criteria. Backend tests must reach the course target of at least 60% coverage. Provider failures must result in either explicitly labeled cached data or an actionable error. The final assessment includes the student's own demonstration, review evidence, and reflection, which cannot be replaced by this proposal.
