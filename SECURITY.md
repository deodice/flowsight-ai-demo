# Security policy

## Reporting a vulnerability

Please do not disclose a vulnerability, credential, exploit, customer record, or
other sensitive evidence in a public issue.

Use
[GitHub private vulnerability reporting](https://github.com/deodice/flowsight-ai-demo/security/advisories/new)
to send the repository owner a private report. Include:

- the affected component and revision;
- a minimal reproduction that does not expose third-party data;
- the likely impact and prerequisites;
- any safe containment or remediation recommendation.

Do not test against systems, tenants, accounts, or data you do not own or have
explicit permission to assess.

## Supported state

Security fixes target the current default branch. This repository is a product
prototype and reference implementation, not a supported production service.
Historical revisions, demo credentials, and unmerged branches are not supported
for production use.

## Demo boundary

- The public hosted experience uses fictional browser-side data.
- Demo access controls are convenience gates, not production authentication.
- Seeded demo credentials must never be reused outside local fictional-data
  environments.
- Real customer, carrier, employee, shipment, financial, or regulated data must
  not be entered into the public demo.
- Local and hosted secrets must come from environment or platform secret
  storage, never committed files.

## Production expectations

Before a production deployment, complete an authorization and tenant-isolation
review, managed identity and MFA design, key rotation, distributed rate
limiting, audit-log retention, backup restoration tests, dependency and code
scanning, incident response, privacy/data-retention controls, and an independent
penetration test.
