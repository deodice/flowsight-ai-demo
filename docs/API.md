# API and integration guide

Authenticate with `POST /v1/auth/login`, then send `Authorization: Bearer <token>`.

Tenant API ingestion uses `X-Tenant-API-Key` and accepts a JSON array at `POST /v1/ingest/{entity_type}`. File onboarding uses multipart upload:

1. `POST /v1/imports/preview`
2. `POST /v1/imports/validate-mapping`
3. `POST /v1/imports`
4. Poll the import job status in the production worker implementation.

Starter entity types are `inventory_snapshot`, `purchase_orders`, `sales_orders`, `shipments`, `receipts`, `sku_master`, and `supplier_master`.

Connector implementations must emit canonical `ConnectorRecord` objects. ERP, WMS, TMS, e-commerce, and accounting slots are reserved without coupling the domain layer to a vendor SDK.

## Freight Ops

- `GET /v1/freight/dashboard`: mode, tender, margin, service, and receivables summary.
- `GET|POST /v1/freight/carriers`: carrier network and profile creation.
- `GET|POST /v1/freight/opportunities`: procurement opportunity queue and creation.
- `GET /v1/freight/opportunities/{id}`: complete sourcing workspace.
- `POST /v1/freight/opportunities/{id}/match`: score all eligible carriers with an auditable breakdown.
- `POST /v1/freight/opportunities/{id}/shortlist`: select carriers for outreach.
- `POST /v1/freight/opportunities/{id}/rfqs/generate`: create copy-ready RFQ subject and body text.
- `PATCH /v1/freight/opportunity-carriers/{id}/status`: track sent, response, no-bid, quote, and award states.
- `POST /v1/freight/opportunities/{id}/bids`: record carrier quote details.
- `GET /v1/freight/opportunities/{id}/comparison`: compare eligible bids and return an explainable recommendation.
- `POST /v1/freight/opportunities/{id}/award`: store the selected bid, score snapshot, and human rationale.
- `GET /v1/freight/opportunities/{id}/procurement-summary.md`: export the decision record.
- `GET|POST /v1/freight/tenders`: tenant-scoped tender board and tender creation.
- `PATCH /v1/freight/tenders/{id}/status`: guarded tender transition with audit context.
- `POST /v1/freight/quotes/calculate`: deterministic preview without persistence.
- `POST /v1/freight/quotes`: persist the quote, line items, inputs, and trace.
- `GET|POST /v1/freight/invoices`: invoice list and quote-to-invoice creation.
- `PATCH /v1/freight/invoices/{id}/status`: guarded invoice lifecycle transition.
- `POST /v1/freight/documents`: sanitized tenant-scoped document upload.

Supported modes are `small_parcel`, `ltl`, `tl`, `spot_bid`, `air_freight`, and `other`. Client roles receive an explicit reduced representation: internal carrier intelligence, cost, gross margin, calculation trace, approval policy, and internal notes are omitted server-side.

For the complete generated contract, run the API and open `/docs`.
