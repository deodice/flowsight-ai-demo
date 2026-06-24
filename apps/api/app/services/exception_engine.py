from datetime import date


def stockout_exception(
    sku: str, on_hand: float, allocated: float, avg_daily_demand: float,
    next_receipt_date: date | None, unit_margin: float, threshold_days: int = 14
) -> dict | None:
    available = max(0, on_hand - allocated)
    days_supply = available / avg_daily_demand if avg_daily_demand > 0 else 999
    if days_supply >= threshold_days:
        return None
    days_to_receipt = (next_receipt_date - date.today()).days if next_receipt_date else None
    gap_days = max(0, (days_to_receipt or threshold_days) - days_supply)
    lost_units = gap_days * avg_daily_demand
    confidence = min(99, 72 + gap_days * 3)
    return {
        "exception_type": "likely_stockout",
        "title": f"Stockout likely: {sku}",
        "severity": "critical" if days_supply < 5 else "high",
        "severity_score": round(min(100, 100 - days_supply * 4), 1),
        "confidence_score": round(confidence, 1),
        "estimated_impact": round(lost_units * unit_margin, 2),
        "contributing_factors": [
            {"label": "Available inventory", "value": available},
            {"label": "Average daily demand", "value": avg_daily_demand},
            {"label": "Days of supply", "value": round(days_supply, 1)},
            {"label": "Days to receipt", "value": days_to_receipt},
        ],
        "recommended_action": "Expedite the next receipt, rebalance from another site, or protect inventory for priority orders."
    }
