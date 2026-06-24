from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Any


MONEY = Decimal("0.01")


def cash(value: Decimal | float | int | str) -> Decimal:
    return Decimal(str(value)).quantize(MONEY, rounding=ROUND_HALF_UP)


@dataclass
class FreightQuoteInput:
    mode: str
    origin: str
    destination: str
    distance_miles: float
    weight_lb: float
    pallet_count: int = 0
    equipment: str | None = None
    service_level: str | None = None
    freight_class: str | None = None
    accessorials: list[str] = field(default_factory=list)
    hazmat: bool = False
    target_margin_pct: float = 20
    fuel_surcharge_pct: float = 18.5
    pieces: int = 1
    dimensions_in: list[dict[str, float]] = field(default_factory=list)
    customer_id: str | None = None
    carrier_id: str | None = None
    lane_history: dict[str, float] = field(default_factory=dict)


DEFAULT_RULES: dict[str, dict[str, float]] = {
    "ltl": {"minimum": 285, "per_mile": .48, "per_cwt": 8.9, "margin_floor": 17},
    "tl": {"minimum": 950, "per_mile": 2.08, "margin_floor": 17},
    "spot_bid": {"minimum": 1050, "per_mile": 2.34, "margin_floor": 15},
    "air_freight": {"minimum": 650, "per_kg": 2.82, "origin_fee": 225, "margin_floor": 18, "dim_divisor": 6000},
}

DEFAULT_ACCESSORIALS = {
    "liftgate": Decimal("95"),
    "appointment": Decimal("65"),
    "hazmat": Decimal("175"),
    "inside_delivery": Decimal("125"),
    "residential": Decimal("110"),
    "air_security": Decimal(".18"),
}


def dimensional_weight_kg(dimensions_in: list[dict[str, float]], divisor: float = 6000) -> float:
    cubic_cm = sum(
        float(item.get("length", 0)) * float(item.get("width", 0)) *
        float(item.get("height", 0)) * float(item.get("pieces", 1)) * 16.387064
        for item in dimensions_in
    )
    return cubic_cm / divisor if divisor else 0


def calculate_freight_quote(
    request: FreightQuoteInput,
    mode_rules: dict[str, Any] | None = None,
    accessorial_rules: dict[str, Decimal | float | int] | None = None,
) -> dict:
    mode = request.mode.lower().replace(" ", "_")
    if mode not in DEFAULT_RULES:
        raise ValueError(f"Unsupported freight mode: {request.mode}")
    rules = {**DEFAULT_RULES[mode], **(mode_rules or {})}
    accessorial_rates = {**DEFAULT_ACCESSORIALS, **(accessorial_rules or {})}
    trace: list[dict] = []
    actual_kg = request.weight_lb * .45359237
    dim_kg = dimensional_weight_kg(request.dimensions_in, rules.get("dim_divisor", 6000))
    chargeable_kg = max(actual_kg, dim_kg)

    if mode == "ltl":
        cwt = request.weight_lb / 100
        calculated = Decimal(str(request.distance_miles * rules["per_mile"] + cwt * rules["per_cwt"]))
        basis = f"{request.distance_miles:.0f} mi x ${rules['per_mile']:.2f} + {cwt:.1f} CWT x ${rules['per_cwt']:.2f}"
    elif mode in {"tl", "spot_bid"}:
        historical = request.lane_history.get("median_carrier_cost")
        calculated = Decimal(str(historical if historical else request.distance_miles * rules["per_mile"]))
        basis = f"{'Historical lane median' if historical else f'{request.distance_miles:.0f} mi x ${rules['per_mile']:.2f}/mi'}"
    else:
        calculated = Decimal(str(rules["origin_fee"] + chargeable_kg * rules["per_kg"]))
        basis = f"${rules['origin_fee']:.2f} origin + {chargeable_kg:.1f} chargeable kg x ${rules['per_kg']:.2f}"

    minimum = Decimal(str(rules["minimum"]))
    linehaul = max(minimum, calculated)
    trace.append({"step": "rate_basis", "formula": basis, "amount": float(cash(calculated))})
    trace.append({"step": "minimum_charge", "formula": f"max(calculated, {cash(minimum)})", "amount": float(cash(linehaul))})

    fuel = linehaul * Decimal(str(request.fuel_surcharge_pct / 100))
    trace.append({"step": "fuel", "formula": f"{cash(linehaul)} x {request.fuel_surcharge_pct:.2f}%", "amount": float(cash(fuel))})

    selected = list(dict.fromkeys(request.accessorials + (["hazmat"] if request.hazmat else [])))
    accessorial_lines: list[dict] = []
    accessorial_total = Decimal("0")
    for code in selected:
        rate = Decimal(str(accessorial_rates.get(code, 0)))
        amount = rate * Decimal(str(chargeable_kg)) if code == "air_security" else rate
        accessorial_total += amount
        accessorial_lines.append({"code": code, "description": code.replace("_", " ").title(), "amount": float(cash(amount))})
        trace.append({"step": f"accessorial:{code}", "formula": "tenant accessorial rule", "amount": float(cash(amount))})

    internal_cost = linehaul + fuel + accessorial_total
    target = Decimal(str(request.target_margin_pct / 100))
    if target >= Decimal("0.95"):
        raise ValueError("Target margin must be below 95%")
    client_total = internal_cost / (Decimal("1") - target)
    margin_amount = client_total - internal_cost
    actual_margin_pct = margin_amount / client_total * 100 if client_total else Decimal("0")
    floor = Decimal(str(rules["margin_floor"]))
    requires_approval = actual_margin_pct < floor
    trace.append({
        "step": "margin",
        "formula": f"sell = cost / (1 - {request.target_margin_pct:.2f}%)",
        "amount": float(cash(client_total)),
        "threshold": float(floor),
        "approval_required": requires_approval,
    })

    confidence = 92
    confidence_reasons = ["Active mode rules", "Complete origin/destination", "Fuel index applied"]
    if request.lane_history:
        confidence += 4
        confidence_reasons.append("Historical lane data available")
    if mode == "spot_bid" and not request.lane_history:
        confidence -= 14
        confidence_reasons.append("No historical spot-lane observations")
    if mode == "air_freight" and not request.dimensions_in:
        confidence -= 12
        confidence_reasons.append("Dimensions missing; actual weight used")
    confidence = max(45, min(99, confidence))

    line_items = [
        {"code": "BASE", "description": "Base transportation", "amount": float(cash(linehaul))},
        {"code": "FUEL", "description": f"Fuel surcharge ({request.fuel_surcharge_pct:.2f}%)", "amount": float(cash(fuel))},
        *accessorial_lines,
    ]
    return {
        "mode": mode,
        "currency": "USD",
        "internal_cost": float(cash(internal_cost)),
        "client_total": float(cash(client_total)),
        "margin_amount": float(cash(margin_amount)),
        "margin_pct": round(float(actual_margin_pct), 2),
        "margin_floor_pct": float(floor),
        "requires_approval": requires_approval,
        "line_items": line_items,
        "calculation_trace": trace,
        "confidence_score": confidence,
        "confidence_reasons": confidence_reasons,
        "air_freight": {
            "actual_weight_kg": round(actual_kg, 2),
            "dimensional_weight_kg": round(dim_kg, 2),
            "chargeable_weight_kg": round(chargeable_kg, 2),
        } if mode == "air_freight" else None,
        "explanation": (
            f"The {mode.replace('_', ' ')} quote applies the active deterministic rate basis, "
            f"minimum charge, {request.fuel_surcharge_pct:.2f}% fuel rule, selected accessorials, "
            f"and a {request.target_margin_pct:.2f}% target margin."
        ),
    }


def external_quote_view(result: dict) -> dict:
    allowed = {
        "mode", "currency", "client_total", "line_items", "confidence_score",
        "confidence_reasons", "air_freight", "explanation"
    }
    return {key: value for key, value in result.items() if key in allowed}
