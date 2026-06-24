from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


STATE_REGIONS = {
    "Northeast": {"CT", "DE", "MA", "MD", "ME", "NH", "NJ", "NY", "PA", "RI", "VT"},
    "Southeast": {"AL", "AR", "FL", "GA", "KY", "LA", "MS", "NC", "SC", "TN", "VA", "WV"},
    "Midwest": {"IA", "IL", "IN", "KS", "MI", "MN", "MO", "ND", "NE", "OH", "SD", "WI"},
    "Southwest": {"AZ", "NM", "OK", "TX"},
    "West": {"AK", "CA", "CO", "HI", "ID", "MT", "NV", "OR", "UT", "WA", "WY"},
}


def _value(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _region_fit(regions: list[str], origin: dict, destination: dict) -> bool:
    normalized = {str(region).strip() for region in regions}
    if "Nationwide" in normalized:
        return True
    states = {str(origin.get("state", "")).upper(), str(destination.get("state", "")).upper()}
    for region in normalized:
        if region in STATE_REGIONS and states & STATE_REGIONS[region]:
            return True
        if region.upper() in states:
            return True
    return False


def score_carrier(opportunity: Any, carrier: Any, manual_adjustment: float = 0) -> dict:
    mode = _value(_value(opportunity, "mode"), "value", _value(opportunity, "mode"))
    covered_modes = set(_value(carrier, "covered_modes", []) or [])
    government_required = any([
        _value(opportunity, "government_relevance", False),
        _value(opportunity, "sddc_relevance", False),
        _value(opportunity, "gfm_relevance", False),
    ])
    government_ready = any([
        _value(carrier, "government_business", False),
        _value(carrier, "sddc_registered", False),
        _value(carrier, "gfm_approved", False),
        _value(carrier, "dod_relevant", False),
    ])
    capability_ready = (
        (not _value(opportunity, "hazmat", False) or _value(carrier, "hazmat_capable", False))
        and (not _value(opportunity, "refrigerated", False) or _value(carrier, "refrigerated_capable", False))
    )
    breakdown: list[dict] = []

    def add(label: str, points: float, reason: str) -> None:
        breakdown.append({"label": label, "points": points, "reason": reason})

    add("Mode match", 25 if mode in covered_modes else -25, f"{mode} {'is' if mode in covered_modes else 'is not'} in covered modes")
    if government_required:
        add("Government readiness", 15 if government_ready else -15, "Government/SDDC/GFM indicators reviewed")
    else:
        add("Government readiness", 5 if government_ready else 0, "Useful but not required for this movement")

    region_ready = _region_fit(
        _value(carrier, "regions_served", []) or [],
        _value(opportunity, "origin", {}) or {},
        _value(opportunity, "destination", {}) or {},
    )
    add("Region fit", 15 if region_ready else -5, "Origin/destination compared with service regions")
    add("Special capability", 10 if capability_ready else -20, "Hazmat and temperature requirements checked")

    relationship = _value(carrier, "relationship_status", "unknown")
    relationship_points = {"preferred": 10, "active": 7, "prospect": 2, "unknown": 0, "do_not_use": -50}.get(relationship, 0)
    add("Relationship", relationship_points, relationship.replace("_", " ").title())

    compliance = _value(carrier, "compliance_status", "incomplete")
    compliance_points = {"complete": 15, "review_due": 7, "incomplete": -8, "expired": -30, "blocked": -50}.get(compliance, -8)
    add("Compliance", compliance_points, compliance.replace("_", " ").title())

    prior_awards = int(_value(carrier, "prior_awards", 0) or 0)
    add("Prior awards", min(10, prior_awards * 2), f"{prior_awards} prior award{'s' if prior_awards != 1 else ''}")

    if not _value(carrier, "primary_contact_email"):
        add("Contact completeness", -5, "No RFQ email on file")
    else:
        add("Contact completeness", 5, "RFQ email is available")

    if manual_adjustment:
        add("Manual adjustment", manual_adjustment, "User-entered sourcing judgment")

    score = max(0, min(100, round(sum(item["points"] for item in breakdown), 1)))
    eligible = (
        mode in covered_modes
        and capability_ready
        and relationship != "do_not_use"
        and compliance not in {"expired", "blocked"}
    )
    return {"score": score, "eligible": eligible, "breakdown": breakdown}


def build_rfq(opportunity: Any, carrier: Any, contact_name: str = "Carrier Partner") -> dict:
    mode = _value(_value(opportunity, "mode"), "value", _value(opportunity, "mode"))
    origin = _value(opportunity, "origin", {}) or {}
    destination = _value(opportunity, "destination", {}) or {}
    pickup = _value(opportunity, "pickup_at")
    delivery = _value(opportunity, "delivery_at")
    deadline = _value(opportunity, "quote_deadline")
    dimensions = _value(opportunity, "dimensions", []) or []
    dimension_text = "; ".join(
        f"{item.get('pieces', 1)} pc @ {item.get('length')}x{item.get('width')}x{item.get('height')} in"
        for item in dimensions
    ) or "Not provided"
    requirements = []
    if _value(opportunity, "hazmat", False):
        requirements.append("Hazmat capable")
    if _value(opportunity, "refrigerated", False):
        requirements.append("Temperature controlled")
    if _value(opportunity, "sddc_relevance", False):
        requirements.append("SDDC readiness required")
    if _value(opportunity, "gfm_relevance", False):
        requirements.append("GFM relevance")
    requirements.extend(_value(opportunity, "required_compliance_tags", []) or [])
    carrier_name = _value(carrier, "name", "Carrier")
    subject = f"RFQ: {mode.replace('_', ' ').title()} | {origin.get('city')}, {origin.get('state')} to {destination.get('city')}, {destination.get('state')}"
    body = f"""Hello {contact_name},

Please provide a rate and capacity confirmation for the following freight opportunity:

Opportunity: {_value(opportunity, 'name')}
Program / contract: {_value(opportunity, 'customer_program') or 'N/A'} / {_value(opportunity, 'contract_number') or 'N/A'}
Origin: {origin.get('city')}, {origin.get('state')} {origin.get('postal_code', '')}
Destination: {destination.get('city')}, {destination.get('state')} {destination.get('postal_code', '')}
Pickup: {pickup.isoformat() if pickup else 'TBD'}
Delivery required: {delivery.isoformat() if delivery else 'TBD'}
Mode: {mode.replace('_', ' ').title()}
Commodity: {_value(opportunity, 'commodity')}
Weight: {_value(opportunity, 'weight_lb'):,.0f} lb
Dimensions: {dimension_text}
Special requirements: {', '.join(requirements) if requirements else 'None noted'}
Quote deadline: {deadline.isoformat() if deadline else 'Please respond as soon as possible'}

Please include total rate, fuel, accessorials, transit time, rate expiration, and any exceptions.

Thank you,
[Your name / contact information]
"""
    return {"carrier": carrier_name, "subject": subject, "body": body.strip()}


def recommend_bid(rows: list[dict]) -> dict | None:
    eligible = [row for row in rows if row.get("eligible", True) and row.get("amount") is not None]
    if not eligible:
        return None
    lowest = min(float(row["amount"]) for row in eligible)
    fastest = min(float(row.get("transit_days") or 999) for row in eligible)
    scored = []
    for row in eligible:
        amount = float(row["amount"])
        transit = float(row.get("transit_days") or 999)
        price_score = 40 * lowest / amount if amount else 0
        fit_score = float(row.get("match_score", 0)) * .45
        transit_score = 15 * fastest / transit if transit and transit < 999 else 0
        total = round(price_score + fit_score + transit_score, 1)
        scored.append({**row, "comparison_score": total, "price_score": round(price_score, 1), "transit_score": round(transit_score, 1)})
    winner = max(scored, key=lambda row: (row["comparison_score"], -float(row["amount"])))
    reason_bits = [
        f"a {winner.get('match_score', 0):.0f}/100 carrier-fit score",
        f"a total rate of ${float(winner['amount']):,.0f}",
        f"{float(winner.get('transit_days') or 0):g}-day transit",
        "complete compliance" if winner.get("compliance_status") == "complete" else "acceptable compliance",
    ]
    return {
        "carrier_id": winner["carrier_id"],
        "carrier_name": winner["carrier_name"],
        "bid_id": winner.get("bid_id"),
        "amount": float(winner["amount"]),
        "comparison_score": winner["comparison_score"],
        "explanation": f"Recommended: {winner['carrier_name']} because it combines " + ", ".join(reason_bits) + ".",
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "ranked": sorted(scored, key=lambda row: row["comparison_score"], reverse=True),
    }
