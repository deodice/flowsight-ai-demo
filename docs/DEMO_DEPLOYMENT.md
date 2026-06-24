# Limited-audience demo deployment

This is the shortest safe path for showing FlowSight AI to a small group without installing Docker.

## Recommended demo shape

Deploy the polished web demo first. The freight procurement workflow, carrier matching, RFQ desk, bid comparison, award record, and client-facing freight screens are already available in the browser experience. The deeper FastAPI service and database remain ready for a later production backend deployment, but they are not required for a sales-style demo link.

For a limited audience, use two layers:

1. The built-in FlowSight demo gate configured with environment variables.
2. Your hosting provider's deployment protection if your plan includes it.

## Option A: Vercel web demo

Vercel is the fastest fit for the current Next.js demo.

1. Put this project in a private GitHub repository.
2. In Vercel, add a new project from that repository.
3. Keep the project rooted at the repository root. The included `vercel.json` tells Vercel how to build `apps/web`.
4. Add these environment variables in Vercel before sharing the link:

```text
DEMO_ACCESS_ENABLED=true
DEMO_ACCESS_USERNAME=flowsight
DEMO_ACCESS_PASSWORD=<choose a strong private password>
DEMO_ACCESS_PROTECT_MARKETING=false
```

With `DEMO_ACCESS_PROTECT_MARKETING=false`, visitors can see the landing page, but the demo app, sign-in page, and onboarding page require the private username and password. Set it to `true` if you want the entire site hidden.

5. Deploy and open `/app/freight`.
6. Share the URL plus the private demo username/password only with the invited audience.

## Option B: Vercel CLI from this folder

If you do not want to connect GitHub yet:

```powershell
cd "C:\Users\derek\Documents\Codex\2026-06-22\re"
npm install -g vercel
vercel
vercel env add DEMO_ACCESS_ENABLED
vercel env add DEMO_ACCESS_USERNAME
vercel env add DEMO_ACCESS_PASSWORD
vercel env add DEMO_ACCESS_PROTECT_MARKETING
vercel --prod
```

Use the same environment variable values shown in Option A.

## What to send invitees

Send a short note like this:

```text
Here is the private FlowSight AI demo:
<demo URL>

Demo access:
Username: flowsight
Password: <private password>

Suggested path:
1. Open Freight Procurement.
2. Review open shipment opportunities.
3. Match carriers.
4. Generate RFQs.
5. Compare bids and award the freight.
```

## Important demo caveats

- Do not enter real customer data in the demo environment.
- The browser demo is intentionally seeded with fictional carriers, tenders, quotes, invoices, and government-readiness examples.
- The current public demo workflow does not automatically send external emails.
- For a production pilot with real users, connect the UI to the FastAPI backend, use a managed PostgreSQL database, configure tenant/user authentication, and move files to private object storage.

## Pre-share checklist

- Build passes.
- The deployed `/app/freight` route opens only after the private demo prompt.
- The demo works on desktop and phone.
- Invitees receive the demo script, not just the raw link.
- The password is changed after the demo window closes.
