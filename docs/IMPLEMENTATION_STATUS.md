# Implementation status and evidence boundary

FlowSight AI is a product prototype and reference implementation. This page
separates what can be demonstrated today from what would still be required for
a production service.

## Public hosted experience

The Vercel deployment is a browser-only product demo using fictional data. It
demonstrates interaction design and operational workflows, but it is not
connected to:

- the FastAPI reference backend;
- production identity or tenant administration;
- live ERP, WMS, TMS, carrier, accounting, storage, or billing systems;
- customer or carrier data;
- operational service-level commitments.

The optional demo access gate is a presentation convenience, not a substitute
for production authentication or authorization.

## Repository-backed implementation

The repository contains:

- a Next.js web application with automated component tests and a production
  build;
- a FastAPI reference backend with domain and API tests;
- relational models, migrations, tenant-scoped domain concepts, fictional seed
  data, and local SQLite/PostgreSQL paths;
- deterministic carrier sourcing, pricing, invoicing, forecasting, anomaly,
  exception, and reporting services;
- local Docker orchestration and deployment documentation;
- provider interfaces for storage, connectors, grounded summaries, jobs, and
  commercial features.

These artifacts demonstrate design and implementation direction. They do not
by themselves prove production scale, complete tenant isolation, regulatory
compliance, forecast lift, cost reduction, adoption, or commercial traction.

## Production gaps

Before production use, the project requires at least:

- a dedicated authorization and cross-tenant isolation review;
- managed identity, MFA, session controls, recovery, and key rotation;
- production connector contracts, retries, reconciliation, and observability;
- distributed rate limiting, queue operations, alerting, and service objectives;
- backup, restoration, disaster-recovery, retention, and deletion exercises;
- privacy, data-processing, and customer security documentation;
- billing, entitlement, and webhook hardening;
- independent security testing and operational load testing.

## Claim standard

Use these labels consistently:

- **Implemented:** present in the repository and covered by a cited test or
  reproducible local path.
- **Demonstrated:** visible in the fictional-data interface but not connected to
  production systems.
- **Planned:** described in architecture or roadmap documentation without a
  completed production implementation.
- **Hypothesis:** a pricing, time-savings, risk, adoption, or business-impact
  assumption requiring real-world validation.

Do not convert simulated metrics or product defaults into customer-outcome
claims without an appropriate evaluation.
