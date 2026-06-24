# System architecture and implementation sequence

## Product boundary

FlowSight is an intelligence and action overlay. Source systems remain systems of record. FlowSight ingests file exports or API records, normalizes them, computes transparent signals, and gives people an evidence-linked workflow.

## Folder structure

```text
apps/
  web/                 Next.js app and product UI
  api/
    app/
      main.py          HTTP API and tenant guards
      models.py        normalized SQLAlchemy schema
      services/        KPI, forecast, anomaly, imports, AI, exceptions
      connectors.py    ingestion connector interface
      storage.py       signed S3-compatible object access
      jobs.py          Celery tasks
      seed.py          three realistic demo tenants
    migrations/        Alembic migrations
    tests/             domain and API tests
docs/                  operating, deployment, and sales guides
```

## Data schema

Identity and commercial: tenants, organizations, sites, users, billing accounts, feature flags.

Master data: products, suppliers, customers, carriers.

Transactions: inventory snapshots, purchase orders and lines, sales orders and lines, shipments and lines, receipts.

Freight commercial graph: carrier profiles and compliance documents, freight opportunities, matched and shortlisted carriers, RFQ state, carrier bids, awards, contacts, shippers, consignees, lanes, freight shipments, tenders and revisions, sell-side quotes and line items, rate cards and rules, accessorials, freight invoices and credits, documents, events, and disputes.

Intelligence: forecast runs, anomaly events, exception events, scorecards, AI generations.

Action and governance: tasks, comments, import jobs, import mappings, validation issues, report presets, feedback items, audit logs.

All mutable business tables include `tenant_id`, timestamps, and soft-delete support where appropriate. External identifiers are unique only inside a tenant.

## Backend API surface

- `/v1/auth`: register, login, verification-ready identity.
- `/v1/dashboard`: role-ready KPI and priority brief.
- `/v1/exceptions`: evidence, impact, confidence, recommendations, feedback, resolution.
- `/v1/tasks`: exception-linked action workflow.
- `/v1/imports`: CSV/XLSX preview, mapping validation, import jobs.
- `/v1/forecasts`: backtested model selection, intervals, replenishment guidance.
- `/v1/ai`: deterministic grounded summary provider and future provider adapter.
- `/v1/reports` and `/v1/exports`: branded PDF and CSV.
- `/v1/feedback`: product and recommendation feedback.
- `/v1/ingest`: tenant API-key ingestion.
- `/v1/admin`: platform tenant administration.
- `/v1/freight`: freight dashboard, tenders, deterministic quotes, invoices, workflow transitions, and documents.
- `/v1/freight/opportunities`: procurement opportunity creation, transparent carrier matching, shortlists, RFQ drafts, bids, comparison, award, and summary export.
- `/v1/freight/carriers`: tenant-scoped carrier profiles, modes, government indicators, contacts, relationships, and compliance readiness.

OpenAPI is published automatically at `/docs` and `/openapi.json`.

## Frontend route map

- `/`: marketing and paid-pilot proposition
- `/sign-in`: secure login and one-click demo entry
- `/onboarding`: tenant, data, thresholds, team, first-value flow
- `/app/overview`: daily command center
- `/app/exceptions`
- `/app/inventory`
- `/app/purchase-orders`
- `/app/forecasting`
- `/app/scorecards`
- `/app/tasks`
- `/app/imports`
- `/app/quality`
- `/app/ai`
- `/app/reports`
- `/app/feedback`
- `/app/admin`
- `/app/release-notes`
- `/app/freight`: broker/carrier command center
- `/app/freight-opportunities`: shipment opportunity queue and creation
- `/app/freight-opportunity`: end-to-end procurement workspace
- `/app/freight-carriers`: carrier relationship and compliance network
- `/app/freight-rfqs`: RFQ and response control
- `/app/freight-awards`: procurement decision register
- `/app/freight-operations`: broker/carrier operating analytics
- `/app/freight-tenders`
- `/app/freight-quotes`
- `/app/freight-invoices`
- `/app/freight-client`: client-safe shipper workspace
- `/app/freight-admin`
- `/app/freight-tour`

## Demo data design

The distributor and manufacturer tenants receive three Pennsylvania sites, representative SKUs, forecast-ready demand patterns, and curated exceptions. The freight tenant receives four mode-specific shipments, tenders, quotes, invoices, rate rules, accessorials, and air-freight references.

## Freight workspace boundary

Internal and client users operate on the same canonical records. Authorization and response serialization create different views:

- Internal roles can see buy cost, margin, approval requirements, pricing trace, and internal notes.
- Client roles can see service details, client quote totals, tender history, documents approved for portal use, and invoice status.
- Any new internal field is deny-by-default for client serializers.

Quote calculations are deterministic and versionable. Each result records inputs, rate-card logic, line items, minima, fuel, accessorials, margin policy, approvals, and a human-readable trace. No competitor screen, wording, protected workflow, or proprietary rate logic is copied.

Carrier matching is also deterministic and transparent. The score breakdown records mode fit, government readiness, region fit, special capability, relationship, compliance, prior awards, contact completeness, and any manual adjustment. Award recommendations combine eligible bid price, carrier-fit score, and transit time; the final human decision and rationale are stored separately.

## Forecasting strategy

Each SKU is evaluated with moving average, simple exponential smoothing, Holt-Winters, and Croston. A rolling holdout chooses the lowest WAPE. The response includes all scores, an 80% interval, reorder point, and safety-stock estimate. Sparse demand remains eligible for Croston instead of being forced into a dense-demand model.

## Security posture

- Argon2 password hashing and short-lived signed access tokens.
- Tenant-scoped ORM queries and tenant IDs on all domain records.
- Role guards for platform administration.
- Request validation, basic rate limiting, security headers, and CORS allow-listing.
- Signed object URLs; no public bucket requirement.
- Immutable audit records for workflow mutations.
- Environment-driven secrets and provider credentials.
- AI output logs and citations are modeled for review.

Production hardening should add managed identity, MFA UI, key rotation, a distributed rate limiter, vulnerability scanning, data-retention policies, backup restoration tests, and a third-party penetration test.

## Implementation sequence

1. Prove value: demo tenant, dashboard, exception evidence, tasks, report.
2. Make onboarding repeatable: imports, saved mappings, quality center.
3. Add intelligence depth: forecast selection, anomaly detection, configurable exception rules.
4. Make it commercially operable: roles, plans, flags, audit, branding, feedback.
5. Add connectors only after file onboarding repeatedly converts pilots.
