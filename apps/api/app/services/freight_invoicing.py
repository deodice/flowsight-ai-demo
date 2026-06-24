from datetime import datetime, timezone
from decimal import Decimal

ALLOWED_TRANSITIONS = {
    "draft": {"issued", "voided"},
    "issued": {"sent", "on_hold", "voided"},
    "sent": {"partially_paid", "paid", "past_due", "disputed", "on_hold"},
    "partially_paid": {"paid", "past_due", "disputed", "credited"},
    "past_due": {"partially_paid", "paid", "disputed", "on_hold", "credited"},
    "on_hold": {"sent", "disputed", "voided"},
    "disputed": {"sent", "partially_paid", "paid", "credited", "voided"},
    "credited": {"paid", "voided"},
    "paid": set(),
    "voided": set(),
}


def validate_invoice_transition(current: str, target: str) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())


def aging_bucket(due_at: datetime | None, balance_due: float | Decimal, now: datetime | None = None) -> str:
    if not due_at or Decimal(str(balance_due)) <= 0:
        return "current"
    now = now or datetime.now(timezone.utc)
    if due_at.tzinfo is None:
        due_at = due_at.replace(tzinfo=timezone.utc)
    days = (now - due_at).days
    if days <= 0:
        return "current"
    if days <= 30:
        return "1_30"
    if days <= 60:
        return "31_60"
    if days <= 90:
        return "61_90"
    return "over_90"


def invoice_analytics(invoices: list[dict], now: datetime | None = None) -> dict:
    buckets = {"current": 0.0, "1_30": 0.0, "31_60": 0.0, "61_90": 0.0, "over_90": 0.0}
    quoted = billed = balance = 0.0
    disputes = 0
    for invoice in invoices:
        quoted += float(invoice.get("quoted_total") or 0)
        billed += float(invoice.get("total") or 0)
        invoice_balance = float(invoice.get("balance_due") or 0)
        balance += invoice_balance
        bucket = aging_bucket(invoice.get("due_at"), invoice_balance, now)
        buckets[bucket] += invoice_balance
        disputes += int(invoice.get("status") == "disputed")
    return {
        "invoice_count": len(invoices),
        "quoted_total": round(quoted, 2),
        "billed_total": round(billed, 2),
        "quoted_vs_billed_delta": round(billed - quoted, 2),
        "quoted_vs_billed_pct": round((billed / quoted - 1) * 100, 2) if quoted else 0,
        "open_balance": round(balance, 2),
        "aging": {key: round(value, 2) for key, value in buckets.items()},
        "disputed_count": disputes,
    }
