# Deployment notes

## Limited-audience demo

For a small invited audience, deploy the web demo first and protect it with the included demo access gate:

```text
DEMO_ACCESS_ENABLED=true
DEMO_ACCESS_USERNAME=flowsight
DEMO_ACCESS_PASSWORD=<choose a strong private password>
DEMO_ACCESS_PROTECT_MARKETING=false
```

The repository includes `vercel.json` for a no-Docker Vercel deployment of the Next.js web app. See [DEMO_DEPLOYMENT.md](DEMO_DEPLOYMENT.md) for the short, non-enterprise path.

## AWS production reference

Recommended low-operations footprint:

- Next.js container on ECS Fargate behind CloudFront and an ALB.
- FastAPI and Celery containers on ECS Fargate.
- RDS PostgreSQL Multi-AZ, ElastiCache Redis, and private S3 buckets.
- SES for scheduled summaries; Stripe Billing for subscriptions.
- Secrets Manager, KMS, CloudWatch logs/alarms, WAF, and GuardDuty.

Run migrations as a one-off deployment task before replacing API containers. Use separate task roles for web, API, and workers. Restrict S3 keys by tenant prefix. Keep RDS and Redis private. Enforce TLS at the load balancer, rotate signing secrets, and test point-in-time database restoration.

Scale workers independently from HTTP services. Forecast refreshes and imports are idempotent jobs; use tenant and source identifiers as deduplication keys.
