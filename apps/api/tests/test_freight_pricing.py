from app.services.freight_pricing import (
    FreightQuoteInput, calculate_freight_quote, external_quote_view
)


def test_tl_quote_is_deterministic_and_traceable():
    request = FreightQuoteInput(
        mode="tl", origin="Harrisburg, PA", destination="Nashville, TN",
        distance_miles=718, weight_lb=38200, target_margin_pct=20,
        fuel_surcharge_pct=18.5, accessorials=["appointment"]
    )
    first = calculate_freight_quote(request)
    second = calculate_freight_quote(request)
    assert first == second
    assert first["client_total"] > first["internal_cost"]
    assert first["margin_pct"] == 20
    assert first["requires_approval"] is False
    assert [step["step"] for step in first["calculation_trace"]] == [
        "rate_basis", "minimum_charge", "fuel", "accessorial:appointment", "margin"
    ]


def test_spot_margin_floor_requires_approval():
    result = calculate_freight_quote(FreightQuoteInput(
        mode="spot_bid", origin="Pittsburgh, PA", destination="Dallas, TX",
        distance_miles=1230, weight_lb=44000, target_margin_pct=12
    ))
    assert result["requires_approval"] is True
    assert result["margin_floor_pct"] == 15


def test_air_freight_uses_greater_chargeable_weight():
    result = calculate_freight_quote(FreightQuoteInput(
        mode="air_freight", origin="PHL", destination="FRA",
        distance_miles=3900, weight_lb=220, target_margin_pct=20,
        dimensions_in=[{"length": 80, "width": 60, "height": 55, "pieces": 2}],
        accessorials=["air_security"]
    ))
    air = result["air_freight"]
    assert air["dimensional_weight_kg"] > air["actual_weight_kg"]
    assert air["chargeable_weight_kg"] == air["dimensional_weight_kg"]


def test_external_quote_view_removes_cost_and_margin():
    result = calculate_freight_quote(FreightQuoteInput(
        mode="ltl", origin="York, PA", destination="Charlotte, NC",
        distance_miles=470, weight_lb=4200, target_margin_pct=20
    ))
    external = external_quote_view(result)
    assert "client_total" in external
    assert "internal_cost" not in external
    assert "margin_pct" not in external
    assert "calculation_trace" not in external
