from types import SimpleNamespace

from app.services.procurement import build_rfq, recommend_bid, score_carrier


def test_carrier_match_score_is_transparent_and_blocks_bad_fit():
    opportunity = SimpleNamespace(
        mode=SimpleNamespace(value="tl"),
        origin={"state": "PA"}, destination={"state": "TN"},
        government_relevance=True, sddc_relevance=True, gfm_relevance=False,
        hazmat=True, refrigerated=False,
    )
    preferred = SimpleNamespace(
        covered_modes=["tl", "ltl"], government_business=True, sddc_registered=True,
        gfm_approved=False, dod_relevant=True, regions_served=["Northeast", "Southeast"],
        hazmat_capable=True, refrigerated_capable=False, relationship_status="preferred",
        compliance_status="complete", prior_awards=4, primary_contact_email="capacity@example.test",
    )
    blocked = SimpleNamespace(
        covered_modes=["ltl"], government_business=False, sddc_registered=False,
        gfm_approved=False, dod_relevant=False, regions_served=["West"],
        hazmat_capable=False, refrigerated_capable=False, relationship_status="do_not_use",
        compliance_status="expired", prior_awards=0, primary_contact_email=None,
    )
    good = score_carrier(opportunity, preferred)
    bad = score_carrier(opportunity, blocked)
    assert good["score"] >= 80
    assert good["eligible"] is True
    assert any(item["label"] == "Compliance" for item in good["breakdown"])
    assert bad["eligible"] is False
    assert bad["score"] == 0


def test_rfq_contains_operating_details_and_recommendation_is_explainable():
    opportunity = SimpleNamespace(
        name="Depot replenishment", customer_program="DLA support",
        contract_number="DEMO-42", mode=SimpleNamespace(value="tl"),
        origin={"city": "Harrisburg", "state": "PA", "postal_code": "17101"},
        destination={"city": "Nashville", "state": "TN", "postal_code": "37201"},
        pickup_at=None, delivery_at=None, quote_deadline=None,
        commodity="Hydraulic assemblies", weight_lb=38200,
        dimensions=[{"pieces": 24, "length": 48, "width": 40, "height": 52}],
        hazmat=False, refrigerated=False, sddc_relevance=True, gfm_relevance=True,
        required_compliance_tags=["Cargo insurance"],
    )
    carrier = SimpleNamespace(name="Keystone Freight Partners")
    rfq = build_rfq(opportunity, carrier, "Jordan")
    assert "Harrisburg" in rfq["body"]
    assert "38,200 lb" in rfq["body"]
    assert "SDDC readiness required" in rfq["body"]

    recommendation = recommend_bid([
        {"carrier_id": "a", "carrier_name": "Carrier A", "bid_id": "1", "amount": 2800,
         "transit_days": 2, "match_score": 94, "compliance_status": "complete", "eligible": True},
        {"carrier_id": "b", "carrier_name": "Carrier B", "bid_id": "2", "amount": 2600,
         "transit_days": 4, "match_score": 71, "compliance_status": "complete", "eligible": True},
    ])
    assert recommendation
    assert recommendation["carrier_name"] == "Carrier A"
    assert "Recommended:" in recommendation["explanation"]
