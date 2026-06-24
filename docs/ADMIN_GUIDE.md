# Admin guide

Tenant admins manage users, roles, branding, thresholds, schedules, mappings, and tenant feature flags. Platform super admins additionally manage tenants, demo workspaces, plan limits, failed jobs, feedback, and system health.

Freight tenants also manage rate cards, lane and customer overrides, fuel and minimum rules, accessorials, approval floors, tender workflows, invoice transitions, portal visibility, and mode-specific fields. Operational roles include Sales/Quote Desk, Dispatch/Execution, Billing/Finance, Read-only Client, and Read-only Partner.

Client and partner roles must never receive internal buy cost, target or actual margin, pricing traces, internal notes, or unapproved documents. Treat portal visibility as a server-side authorization rule, not merely a hidden UI element.

Impersonation should always create an audit record that includes the platform actor, target tenant, start time, end time, and reason. Do not expose password hashes, billing secrets, object-storage keys, or raw AI provider credentials in admin responses.

Plan defaults:

| Plan | Sites | Users | Refresh | Forecast | AI | White label | API |
|---|---:|---:|---|---|---|---|---|
| Pilot | 1 | 5 | Daily | Limited | Weekly | No | No |
| Starter | 1 | 5 | Daily | No | Weekly | No | No |
| Growth | 3 | 25 | Hourly | Yes | Yes | No | No |
| Scale | Configurable | Configurable | Hourly | Yes | Yes | Yes | Yes |

Freight packaging defaults:

| Plan | Monthly | Intended use |
|---|---:|---|
| Starter | $249 | Small broker, carrier, or owner-operator quote and tender workflow |
| Growth | $599 | Team workflows, invoicing analytics, rules, and client portal |
| Pro | $1,250 | Multi-entity controls, advanced governance, accounting adapters, and priority support |
