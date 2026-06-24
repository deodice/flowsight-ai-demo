def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_internal_dashboard_includes_margin(client, freight_token):
    response = client.get("/v1/freight/dashboard", headers=auth(freight_token))
    assert response.status_code == 200
    body = response.json()
    assert body["loads"] == 4
    assert "gross_margin_pct" in body
    assert body["mode_mix"]["air_freight"] == 1
    assert body["procurement"]["open_opportunities"] == 3
    assert body["procurement"]["quotes_received"] == 3


def test_client_dashboard_and_tenders_hide_internal_financials(client, client_token):
    dashboard = client.get("/v1/freight/dashboard", headers=auth(client_token)).json()
    assert dashboard["workspace"] == "client"
    assert "internal_cost" not in dashboard
    assert "gross_margin" not in dashboard
    tenders = client.get("/v1/freight/tenders", headers=auth(client_token)).json()
    assert tenders
    assert all("internal_cost" not in item for item in tenders)
    assert all("internal_notes" not in item for item in tenders)


def test_client_quote_calculation_is_reduced(client, client_token):
    response = client.post("/v1/freight/quotes/calculate", headers=auth(client_token), json={
        "mode": "tl", "origin": "Harrisburg, PA", "destination": "Nashville, TN",
        "distance_miles": 718, "weight_lb": 38200, "target_margin_pct": 20
    })
    assert response.status_code == 200
    body = response.json()
    assert "client_total" in body
    assert "internal_cost" not in body
    assert "calculation_trace" not in body


def test_client_cannot_create_carrier_quote(client, client_token):
    response = client.post("/v1/freight/quotes", headers=auth(client_token), json={
        "mode": "ltl", "origin": "York, PA", "destination": "Charlotte, NC",
        "distance_miles": 470, "weight_lb": 4200, "target_margin_pct": 20
    })
    assert response.status_code == 403


def test_internal_quote_creation_and_invoice_summary(client, freight_token):
    quote = client.post("/v1/freight/quotes", headers=auth(freight_token), json={
        "mode": "spot_bid", "origin": "Pittsburgh, PA", "destination": "Dallas, TX",
        "distance_miles": 1230, "weight_lb": 44000, "target_margin_pct": 12,
        "lane_history": {"median_carrier_cost": 3385}
    })
    assert quote.status_code == 201
    assert quote.json()["requires_approval"] is True
    invoices = client.get("/v1/freight/invoices", headers=auth(freight_token))
    assert invoices.status_code == 200
    assert invoices.json()["analytics"]["invoice_count"] == 4


def test_procurement_workflow_from_opportunity_to_award_and_export(client, freight_token):
    headers = auth(freight_token)
    carriers = client.get("/v1/freight/carriers", headers=headers)
    assert carriers.status_code == 200
    assert len(carriers.json()) >= 7
    assert any(row["sddc_registered"] for row in carriers.json())

    created = client.post("/v1/freight/opportunities", headers=headers, json={
        "name": "Urgent depot replenishment",
        "customer_program": "DLA support",
        "contract_number": "DEMO-SP4701-26-D-0220",
        "origin": {"city": "Harrisburg", "state": "PA", "postal_code": "17101"},
        "destination": {"city": "Nashville", "state": "TN", "postal_code": "37201"},
        "pickup_at": "2026-06-28T12:00:00Z",
        "delivery_at": "2026-06-30T21:00:00Z",
        "quote_deadline": "2026-06-24T18:00:00Z",
        "mode": "tl", "weight_lb": 38200,
        "dimensions": [{"pieces": 24, "length": 48, "width": 40, "height": 52}],
        "commodity": "Hydraulic assemblies",
        "government_relevance": True, "sddc_relevance": True, "gfm_relevance": True,
        "required_compliance_tags": ["Active authority", "Cargo insurance", "SDDC readiness"],
        "required_documents": ["Operating authority", "Cargo insurance", "W-9"],
        "priority": "urgent",
    })
    assert created.status_code == 201
    opportunity_id = created.json()["id"]

    matched = client.post(f"/v1/freight/opportunities/{opportunity_id}/match", headers=headers)
    assert matched.status_code == 200
    eligible = [row for row in matched.json() if row["eligible"]]
    assert len(eligible) >= 3
    assert eligible[0]["match_score"] >= eligible[1]["match_score"]
    assert eligible[0]["score_breakdown"]

    shortlist_ids = [row["carrier_id"] for row in eligible[:3]]
    shortlisted = client.post(
        f"/v1/freight/opportunities/{opportunity_id}/shortlist",
        headers=headers, json={"carrier_ids": shortlist_ids},
    )
    assert shortlisted.status_code == 200

    generated = client.post(
        f"/v1/freight/opportunities/{opportunity_id}/rfqs/generate",
        headers=headers, json={},
    )
    assert generated.status_code == 200
    rfqs = generated.json()["rfqs"]
    assert len(rfqs) == 3
    assert "Quote deadline" in rfqs[0]["body"]

    for rfq in rfqs:
        response = client.patch(
            f"/v1/freight/opportunity-carriers/{rfq['opportunity_carrier_id']}/status",
            headers=headers, json={"status": "rfq_sent"},
        )
        assert response.status_code == 200

    for index, carrier_id in enumerate(shortlist_ids):
        bid = client.post(
            f"/v1/freight/opportunities/{opportunity_id}/bids",
            headers=headers, json={
                "carrier_id": carrier_id, "amount": 2825 + index * 90,
                "transit_days": 2 + index, "fuel_surcharge": 0,
                "carrier_contact": "Demo capacity desk",
                "notes": "Capacity confirmed and all-in rate.",
            },
        )
        assert bid.status_code == 201

    comparison = client.get(
        f"/v1/freight/opportunities/{opportunity_id}/comparison", headers=headers
    )
    assert comparison.status_code == 200
    recommendation = comparison.json()["recommendation"]
    assert recommendation
    assert "Recommended:" in recommendation["explanation"]

    award = client.post(
        f"/v1/freight/opportunities/{opportunity_id}/award",
        headers=headers, json={
            "carrier_id": recommendation["carrier_id"],
            "bid_id": recommendation["bid_id"],
            "rationale": recommendation["explanation"],
        },
    )
    assert award.status_code == 201
    assert award.json()["carrier_id"] == recommendation["carrier_id"]

    summary = client.get(
        f"/v1/freight/opportunities/{opportunity_id}/procurement-summary.md",
        headers=headers,
    )
    assert summary.status_code == 200
    assert "text/markdown" in summary.headers["content-type"]
    assert "Bid comparison" in summary.text
    assert award.json()["carrier_name"] in summary.text


def test_client_role_cannot_access_internal_carrier_procurement(client, client_token):
    headers = auth(client_token)
    assert client.get("/v1/freight/carriers", headers=headers).status_code == 403
    assert client.get("/v1/freight/opportunities", headers=headers).status_code == 403
