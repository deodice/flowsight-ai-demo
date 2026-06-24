from datetime import datetime, timedelta, timezone
from app.services.freight_invoicing import aging_bucket, invoice_analytics, validate_invoice_transition


def test_invoice_workflow_transitions_are_guarded():
    assert validate_invoice_transition("draft", "issued")
    assert validate_invoice_transition("sent", "disputed")
    assert not validate_invoice_transition("paid", "draft")
    assert not validate_invoice_transition("draft", "paid")


def test_invoice_aging_and_variance_summary():
    now = datetime(2026, 6, 22, tzinfo=timezone.utc)
    rows = [
        {"due_at": now + timedelta(days=5), "balance_due": 1000, "quoted_total": 900, "total": 1000, "status": "sent"},
        {"due_at": now - timedelta(days=45), "balance_due": 2000, "quoted_total": 1800, "total": 2000, "status": "disputed"},
    ]
    assert aging_bucket(rows[1]["due_at"], 2000, now) == "31_60"
    summary = invoice_analytics(rows, now)
    assert summary["open_balance"] == 3000
    assert summary["aging"]["current"] == 1000
    assert summary["aging"]["31_60"] == 2000
    assert summary["quoted_vs_billed_delta"] == 300
    assert summary["disputed_count"] == 1
