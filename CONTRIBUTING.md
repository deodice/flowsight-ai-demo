# Contributing

Thank you for helping improve FlowSight AI. Keep changes focused, reviewable,
and honest about the prototype boundary.

## Workflow

1. Create a focused branch from the latest `main`.
2. Use a conventional commit such as `fix:`, `feat:`, `docs:`, `test:`, or
   `chore(ci):`.
3. Add or update tests and documentation with behavior changes.
4. Open a draft pull request with a concise summary, risk notes, and exact
   verification results.
5. Use squash merge after required checks and review are complete.

## Local setup

Follow the [README](README.md) for native or Docker-based setup. Keep
dependencies in the existing pnpm lockfile and Python requirements file. Do not
silently regenerate dependency state with a different package-manager version.

## Verification

For web changes:

```powershell
pnpm install --frozen-lockfile
pnpm lint
pnpm test
pnpm build
pnpm audit --prod
```

For API changes, after activating a virtual environment:

```powershell
python -m pip install -r apps\api\requirements.txt
$env:PYTHONPATH="apps/api"
python -m pytest apps\api\tests --cov=apps/api/app
python -m pip_audit -r apps\api\requirements.txt
```

Run `git diff --check` before requesting review.

## Data and security

- Use only fictional, synthetic, or properly licensed data in examples.
- Never commit credentials, customer data, production exports, local databases,
  or private keys.
- Preserve tenant scope in queries, schemas, serializers, tasks, exports, and
  tests.
- Treat new fields as client-hidden until an explicit serializer and
  authorization decision is reviewed.
- Keep prices, predictions, and recommendations explainable and label simulated
  outcomes as simulations.
- Report vulnerabilities through [SECURITY.md](SECURITY.md), not a public
  issue.

## Licensing

No repository-wide open-source license has been selected. A contribution does
not by itself grant rights to use or redistribute the repository. Do not add or
change licensing terms in an ordinary feature pull request.
