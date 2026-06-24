from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy import select
from .database import Base, SessionLocal, engine
from .models import (
    AccessorialRule, BillingAccount, Carrier, CarrierBid, CarrierComplianceDocument,
    Consignee, Contact, Customer, ExceptionEvent, ExceptionStatus, FeatureFlag,
    FreightAward, FreightInvoice, FreightInvoiceStatus, FreightOpportunity, FreightQuote,
    FreightShipment, FreightTender, InvoiceLineItem, Lane, LoadMode, OpportunityCarrier,
    OpportunityCarrierStatus, OpportunityStatus, Organization, Plan, Product, QuoteLineItem,
    RateCard, RateRule, Role, Shipper, Site, Supplier, TenderStatus, Tenant, User
)
from .security import hash_password
from .services.procurement import build_rfq, score_carrier


def seed_tenant(db, name: str, slug: str, business_type: str):
    existing = db.scalar(select(Tenant).where(Tenant.slug == slug))
    if existing:
        return existing
    tenant = Tenant(
        name=name, slug=slug, business_type=business_type, plan=Plan.growth, is_demo=True,
        config={"stockout_days": 14, "backorder_days": 7, "price_variance_pct": 8, "api_key": f"demo-{slug}"}
    )
    db.add(tenant); db.flush()
    org = Organization(tenant_id=tenant.id, name=name.replace(" Demo", ""))
    db.add(org); db.flush()
    sites = [
        Site(tenant_id=tenant.id, organization_id=org.id, code="HBG", name="Harrisburg DC", city="Harrisburg", state="PA"),
        Site(tenant_id=tenant.id, organization_id=org.id, code="PIT", name="Pittsburgh DC", city="Pittsburgh", state="PA"),
        Site(tenant_id=tenant.id, organization_id=org.id, code="ALN", name="Allentown DC", city="Allentown", state="PA"),
    ]
    db.add_all(sites)
    user = User(
        tenant_id=tenant.id, email="maya@demo.flowsight.ai", full_name="Maya Chen",
        password_hash=hash_password("FlowSightDemo!"), role=Role.tenant_admin, verified=True
    )
    db.add(user); db.flush()
    products = [
        Product(tenant_id=tenant.id, sku="HX-440", name="Hydraulic Coupler", category="Hydraulics", unit_cost=Decimal("38.40"), unit_price=Decimal("84.00"), lead_time_days=18),
        Product(tenant_id=tenant.id, sku="BRG-220", name="Sealed Bearing Assembly", category="Bearings", unit_cost=Decimal("21.12"), unit_price=Decimal("48.50"), lead_time_days=14),
        Product(tenant_id=tenant.id, sku="VLV-110", name="Stainless Control Valve", category="Valves", unit_cost=Decimal("64.20"), unit_price=Decimal("139.00"), lead_time_days=24),
    ]
    db.add_all(products)
    db.add_all([
        Supplier(tenant_id=tenant.id, code="KEY", name="Keystone Components", planned_lead_time_days=12),
        Supplier(tenant_id=tenant.id, code="NEC", name="Northeast Castings", planned_lead_time_days=18),
    ])
    risks = [
        ("EX-1048","likely_stockout","Stockout likely: HX-440 Hydraulic Coupler","3.2 days of supply remain; next confirmed receipt is 9 days away.","critical",96,94,42800,["On hand: 86 units","Avg demand: 27/day","PO 8841 expected Jun 30"],[{"type":"sku","id":"HX-440"},{"type":"po","id":"8841"}],"Expedite 220 units on PO 8841 and rebalance 60 units from Harrisburg."),
        ("EX-1044","late_purchase_order","PO 8836 likely 11 days late","Northeast Castings is trending beyond its historical lead-time band.","critical",91,89,31500,["Supplier median: 18 days","Current elapsed: 27 days","No ASN received"],[{"type":"po","id":"8836"}],"Request supplier commit date and qualify the alternate source."),
        ("EX-1039","aging_backorder","Backorder cluster aging above SLA","12 customer lines have aged beyond 7 days, concentrated in two SKUs.","high",82,97,22100,["12 lines affected","Oldest: 16 days","4 key accounts impacted"],[{"type":"order_lines","count":12}],"Prioritize available stock by customer tier and notify account owners."),
        ("EX-1032","price_variance","Purchase price variance on BRG-220","Unit cost increased 14.8%, outside the tenant threshold of 8%.","high",76,99,17800,["Previous: $18.40","Current: $21.12","Annualized: +$17.8k"],[{"type":"sku","id":"BRG-220"}],"Validate the price break and compare the secondary supplier quote."),
        ("EX-1026","carrier_delay","Carrier OTIF deterioration: RoadStar","OTIF fell below 90% for the third consecutive week.","medium",62,92,9400,["Current OTIF: 86.4%","Baseline: 94.8%","31 shipments"],[{"type":"carrier","id":"RoadStar"}],"Open a carrier review and shift priority lanes to Keystone Freight."),
    ]
    for code, kind, title, detail, severity, score, confidence, impact, factors, related, action in risks:
        db.add(ExceptionEvent(
            tenant_id=tenant.id, code=code, exception_type=kind, title=title, detail=detail,
            severity=severity, severity_score=score, confidence_score=confidence,
            estimated_impact=Decimal(str(impact)), contributing_factors=factors, related_records=related,
            recommended_action=action, status=ExceptionStatus.open, owner_id=user.id,
            due_at=datetime.now(timezone.utc) + timedelta(days=1)
        ))
    db.add(BillingAccount(tenant_id=tenant.id, plan=Plan.growth, status="active", entitlements={"sites":3,"users":25,"forecasting":True,"ai":True,"white_label":False,"api":False}))
    for key, enabled in [("ai_briefings",True),("advanced_forecasting",True),("white_label_reports",False),("api_access",False)]:
        db.add(FeatureFlag(tenant_id=tenant.id, key=key, enabled=enabled))
    db.commit()
    return tenant


def seed_freight_data(db, tenant: Tenant):
    if db.scalar(select(FreightTender).where(FreightTender.tenant_id == tenant.id)):
        return
    user = db.scalar(select(User).where(User.tenant_id == tenant.id))
    customer = Customer(tenant_id=tenant.id, code="APEX", name="Apex Machine Works", tier="strategic")
    carrier = Carrier(tenant_id=tenant.id, code="KFP", name="Keystone Freight Partners")
    shipper = Shipper(
        tenant_id=tenant.id, code="APEX-HBG", name="Apex Machine Works - Harrisburg",
        address={"city": "Harrisburg", "state": "PA", "postal_code": "17101"}
    )
    consignee = Consignee(
        tenant_id=tenant.id, code="APEX-BNA", name="Apex Nashville Receiving",
        address={"city": "Nashville", "state": "TN", "postal_code": "37201"},
        appointment_required=True
    )
    lane = Lane(
        tenant_id=tenant.id, code="HBG-BNA",
        origin={"city": "Harrisburg", "state": "PA"},
        destination={"city": "Nashville", "state": "TN"},
        distance_miles=718, default_mode=LoadMode.tl
    )
    db.add_all([customer, carrier, shipper, consignee, lane]); db.flush()

    modes = [LoadMode.tl, LoadMode.air_freight, LoadMode.ltl, LoadMode.spot_bid]
    statuses = [TenderStatus.awarded, TenderStatus.countered, TenderStatus.issued, TenderStatus.accepted]
    values = [(2840, 2245), (6425, 5180), (1185, 942), (3975, 3385)]
    for index, mode in enumerate(modes, start=1):
        shipment = FreightShipment(
            tenant_id=tenant.id, shipment_number=f"SHP-88{20 + index}",
            customer_id=customer.id, carrier_id=carrier.id, shipper_id=shipper.id,
            consignee_id=consignee.id, lane_id=lane.id, mode=mode,
            status="planned" if index > 1 else "in_transit",
            equipment="Priority Air" if mode == LoadMode.air_freight else "53' Dry Van",
            service_level="Priority" if mode == LoadMode.air_freight else "Standard",
            weight_lb=4062 if mode == LoadMode.air_freight else 38200,
            pallet_count=4 if mode == LoadMode.air_freight else 24,
            pickup_at=datetime.now(timezone.utc) + timedelta(days=index),
            delivery_at=datetime.now(timezone.utc) + timedelta(days=index + 2),
            mawb_number="074-38192044" if mode == LoadMode.air_freight else None,
            hawb_number="KFP-882941" if mode == LoadMode.air_freight else None,
            origin_airport="PHL" if mode == LoadMode.air_freight else None,
            destination_airport="FRA" if mode == LoadMode.air_freight else None,
            actual_weight_kg=1842.5 if mode == LoadMode.air_freight else None,
            dimensional_weight_kg=1796.2 if mode == LoadMode.air_freight else None,
            chargeable_weight_kg=1842.5 if mode == LoadMode.air_freight else None,
            internal_cost=Decimal(str(values[index-1][1])),
            client_charge=Decimal(str(values[index-1][0])),
            internal_notes="Preferred carrier capacity confirmed."
        )
        db.add(shipment); db.flush()
        quoted, cost = values[index-1]
        margin_pct = round((quoted - cost) / quoted * 100, 2)
        tender = FreightTender(
            tenant_id=tenant.id, tender_number=f"TND-20{80 + index}",
            shipment_id=shipment.id, customer_id=customer.id, carrier_id=carrier.id,
            lane_id=lane.id, mode=mode, status=statuses[index-1],
            issued_at=datetime.now(timezone.utc) - timedelta(hours=index * 2),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=8 + index),
            quoted_amount=Decimal(str(quoted)), internal_cost=Decimal(str(cost)),
            target_margin_pct=margin_pct, owner_id=user.id,
            client_notes="Standard service terms apply.",
            internal_notes="Review spot margin before issue." if mode == LoadMode.spot_bid else "Within policy."
        )
        db.add(tender); db.flush()
        quote = FreightQuote(
            tenant_id=tenant.id, quote_number=f"Q-31{20 + index}",
            tender_id=tender.id, customer_id=customer.id, carrier_id=carrier.id,
            lane_id=lane.id, mode=mode, status="ready",
            valid_until=tender.expires_at, internal_cost=Decimal(str(cost)),
            client_total=Decimal(str(quoted)), margin_amount=Decimal(str(quoted - cost)),
            margin_pct=margin_pct, requires_approval=margin_pct < (15 if mode == LoadMode.spot_bid else 17),
            calculation_input={"distance_miles": 718, "weight_lb": shipment.weight_lb, "mode": mode.value},
            calculation_trace=[{"step": "seeded_demo", "formula": "demo rate card", "amount": quoted}],
            explanation="Demo quote calculated from the active mode rate card, fuel rule, and margin target."
        )
        db.add(quote); db.flush()
        db.add_all([
            QuoteLineItem(tenant_id=tenant.id, quote_id=quote.id, code="BASE", description="Base transportation", quantity=1, unit_rate=Decimal(str(cost * .82)), amount=Decimal(str(round(cost * .82, 2))), cost_amount=Decimal(str(round(cost * .82, 2)))),
            QuoteLineItem(tenant_id=tenant.id, quote_id=quote.id, code="FUEL", description="Fuel surcharge", quantity=1, unit_rate=Decimal(str(cost * .18)), amount=Decimal(str(round(cost * .18, 2))), cost_amount=Decimal(str(round(cost * .18, 2)))),
        ])
        invoice = FreightInvoice(
            tenant_id=tenant.id, invoice_number=f"INV-104{80-index}",
            shipment_id=shipment.id, tender_id=tender.id, quote_id=quote.id,
            customer_id=customer.id,
            status=[FreightInvoiceStatus.sent, FreightInvoiceStatus.issued, FreightInvoiceStatus.past_due, FreightInvoiceStatus.partially_paid][index-1],
            issued_at=datetime.now(timezone.utc) - timedelta(days=index * 12),
            due_at=datetime.now(timezone.utc) + timedelta(days=20 - index * 12),
            quoted_total=Decimal(str(quoted)), subtotal=Decimal(str(quoted + 85)),
            total=Decimal(str(quoted + 85)),
            amount_paid=Decimal("0") if index < 4 else Decimal(str(quoted)),
            balance_due=Decimal(str(quoted + 85)) if index < 4 else Decimal("85")
        )
        db.add(invoice); db.flush()
        db.add(InvoiceLineItem(
            tenant_id=tenant.id, invoice_id=invoice.id, code="FREIGHT",
            description="Freight transportation", quantity=1,
            unit_rate=Decimal(str(quoted)), amount=Decimal(str(quoted))
        ))
        db.add(InvoiceLineItem(
            tenant_id=tenant.id, invoice_id=invoice.id, code="APPT",
            description="Delivery appointment", quantity=1,
            unit_rate=Decimal("85"), amount=Decimal("85")
        ))

    rate_card = RateCard(
        tenant_id=tenant.id, name="Apex Machine Works TL", scope_type="customer",
        scope_id=customer.id, mode=LoadMode.tl, version=4,
        effective_from=date.today() - timedelta(days=21),
        config={"basis": "per_mile", "rate": 2.08, "minimum": 950, "fuel_index": "doe_weekly", "margin_floor": 17}
    )
    db.add(rate_card); db.flush()
    db.add(RateRule(
        tenant_id=tenant.id, rate_card_id=rate_card.id, name="PA to Southeast TL override",
        rule_type="lane_override", priority=10,
        conditions={"origin_state": "PA", "destination_region": "Southeast"},
        calculation={"per_mile": 2.14}
    ))
    db.add_all([
        AccessorialRule(tenant_id=tenant.id, rate_card_id=rate_card.id, code="LIFT", description="Liftgate service", charge_type="fixed", amount=Decimal("95")),
        AccessorialRule(tenant_id=tenant.id, rate_card_id=rate_card.id, code="APPT", description="Appointment delivery", charge_type="fixed", amount=Decimal("65")),
        AccessorialRule(tenant_id=tenant.id, rate_card_id=rate_card.id, code="HAZ", description="Hazmat handling", charge_type="fixed", amount=Decimal("175")),
    ])
    db.add(FeatureFlag(tenant_id=tenant.id, key="freight_ops", enabled=True, config={"workspaces": ["internal", "client"], "air_freight": True}))
    db.commit()


def seed_procurement_data(db, tenant: Tenant):
    if db.scalar(select(FreightOpportunity).where(FreightOpportunity.tenant_id == tenant.id)):
        return
    user = db.scalar(select(User).where(User.tenant_id == tenant.id))
    carrier_specs = [
        {
            "code": "KFP", "name": "Keystone Freight Partners", "tier": "strategic",
            "classification": "carrier", "covered_modes": ["ltl", "tl", "spot_bid"],
            "headquarters": {"city": "Harrisburg", "state": "PA"},
            "regions_served": ["Northeast", "Southeast", "Midwest"],
            "government_business": True, "sddc_registered": True, "gfm_approved": True,
            "dod_relevant": True, "primary_contact_name": "Jordan Ellis",
            "primary_contact_email": "jordan.ellis@keystone.demo",
            "primary_contact_phone": "717-555-0142", "authority_status": "active",
            "insurance_expires_on": date.today() + timedelta(days=214),
            "hazmat_capable": True, "refrigerated_capable": False,
            "relationship_status": "preferred", "compliance_status": "complete",
            "performance_score": 96, "prior_awards": 8,
        },
        {
            "code": "BRX", "name": "Blue Ridge Transport", "tier": "preferred",
            "classification": "carrier", "covered_modes": ["ltl", "tl", "spot_bid"],
            "headquarters": {"city": "Roanoke", "state": "VA"},
            "regions_served": ["Northeast", "Southeast"],
            "government_business": False, "sddc_registered": False, "gfm_approved": False,
            "dod_relevant": False, "primary_contact_name": "Taylor Morgan",
            "primary_contact_email": "taylor.morgan@blueridge.demo",
            "primary_contact_phone": "540-555-0127", "authority_status": "active",
            "insurance_expires_on": date.today() + timedelta(days=121),
            "hazmat_capable": True, "refrigerated_capable": True,
            "relationship_status": "active", "compliance_status": "complete",
            "performance_score": 89, "prior_awards": 4,
        },
        {
            "code": "SGL", "name": "Sentinel Government Logistics", "tier": "strategic",
            "classification": "broker", "covered_modes": ["small_parcel", "ltl", "tl", "air_freight", "spot_bid"],
            "headquarters": {"city": "Alexandria", "state": "VA"},
            "regions_served": ["Nationwide"],
            "government_business": True, "sddc_registered": True, "gfm_approved": True,
            "dod_relevant": True, "primary_contact_name": "Morgan Hayes",
            "primary_contact_email": "morgan.hayes@sentinel.demo",
            "primary_contact_phone": "703-555-0181", "authority_status": "active",
            "insurance_expires_on": date.today() + timedelta(days=287),
            "hazmat_capable": True, "refrigerated_capable": True,
            "relationship_status": "active", "compliance_status": "complete",
            "performance_score": 94, "prior_awards": 6,
        },
        {
            "code": "LAC", "name": "Liberty Air Cargo", "tier": "preferred",
            "classification": "carrier", "covered_modes": ["air_freight"],
            "headquarters": {"city": "Philadelphia", "state": "PA"},
            "regions_served": ["Northeast", "Nationwide"],
            "government_business": True, "sddc_registered": False, "gfm_approved": True,
            "dod_relevant": True, "primary_contact_name": "Avery Brooks",
            "primary_contact_email": "avery.brooks@libertyair.demo",
            "primary_contact_phone": "215-555-0168", "authority_status": "active",
            "insurance_expires_on": date.today() + timedelta(days=178),
            "hazmat_capable": True, "refrigerated_capable": False,
            "relationship_status": "active", "compliance_status": "complete",
            "performance_score": 92, "prior_awards": 5,
        },
        {
            "code": "CFL", "name": "Confluence Freight Brokerage", "tier": "standard",
            "classification": "broker", "covered_modes": ["ltl", "tl", "spot_bid"],
            "headquarters": {"city": "Pittsburgh", "state": "PA"},
            "regions_served": ["Northeast", "Midwest"],
            "government_business": False, "sddc_registered": False, "gfm_approved": False,
            "dod_relevant": False, "primary_contact_name": "Casey Reed",
            "primary_contact_email": "casey.reed@confluence.demo",
            "primary_contact_phone": "412-555-0193", "authority_status": "active",
            "insurance_expires_on": date.today() + timedelta(days=64),
            "hazmat_capable": False, "refrigerated_capable": False,
            "relationship_status": "prospect", "compliance_status": "review_due",
            "performance_score": 84, "prior_awards": 1,
        },
        {
            "code": "AOO", "name": "Allegheny Independent Transport", "tier": "community",
            "classification": "owner_operator", "covered_modes": ["tl", "spot_bid"],
            "headquarters": {"city": "Johnstown", "state": "PA"},
            "regions_served": ["PA", "OH", "WV", "MD"],
            "government_business": False, "sddc_registered": False, "gfm_approved": False,
            "dod_relevant": False, "primary_contact_name": "Jamie Cole",
            "primary_contact_email": "jamie.cole@allegheny.demo",
            "primary_contact_phone": "814-555-0119", "authority_status": "active",
            "insurance_expires_on": date.today() + timedelta(days=42),
            "hazmat_capable": False, "refrigerated_capable": False,
            "relationship_status": "prospect", "compliance_status": "incomplete",
            "performance_score": 87, "prior_awards": 0,
        },
        {
            "code": "TNP", "name": "Titan National Parcel", "tier": "standard",
            "classification": "carrier", "covered_modes": ["small_parcel", "ltl"],
            "headquarters": {"city": "Columbus", "state": "OH"},
            "regions_served": ["Nationwide"],
            "government_business": True, "sddc_registered": False, "gfm_approved": False,
            "dod_relevant": True, "primary_contact_name": None,
            "primary_contact_email": None, "primary_contact_phone": None,
            "authority_status": "active",
            "insurance_expires_on": date.today() + timedelta(days=310),
            "hazmat_capable": False, "refrigerated_capable": False,
            "relationship_status": "unknown", "compliance_status": "complete",
            "performance_score": 86, "prior_awards": 2,
        },
    ]
    carriers: dict[str, Carrier] = {}
    for spec in carrier_specs:
        carrier = db.scalar(select(Carrier).where(
            Carrier.tenant_id == tenant.id, Carrier.code == spec["code"]
        ))
        if carrier:
            for key, value in spec.items():
                setattr(carrier, key, value)
        else:
            carrier = Carrier(tenant_id=tenant.id, **spec)
            db.add(carrier)
        db.flush()
        carriers[carrier.code] = carrier
        if carrier.primary_contact_name:
            db.add(Contact(
                tenant_id=tenant.id, carrier_id=carrier.id,
                full_name=carrier.primary_contact_name,
                email=carrier.primary_contact_email, phone=carrier.primary_contact_phone,
                role_title="Capacity and government programs",
            ))
        for document_type in ["operating_authority", "cargo_insurance", "w9"]:
            db.add(CarrierComplianceDocument(
                tenant_id=tenant.id, carrier_id=carrier.id, document_type=document_type,
                status="verified" if carrier.compliance_status == "complete" else "review_due",
                expires_on=carrier.insurance_expires_on if document_type == "cargo_insurance" else None,
                verified_at=datetime.now(timezone.utc) - timedelta(days=14),
            ))

    opportunities = [
        FreightOpportunity(
            tenant_id=tenant.id, opportunity_number="OPP-2417",
            name="DLA depot replenishment movement",
            customer_program="Federal Supply Group / DLA support",
            contract_number="DEMO-SP4701-26-D-0142",
            origin={"city": "Harrisburg", "state": "PA", "postal_code": "17101"},
            destination={"city": "Nashville", "state": "TN", "postal_code": "37201"},
            pickup_at=datetime.now(timezone.utc) + timedelta(days=2),
            delivery_at=datetime.now(timezone.utc) + timedelta(days=4),
            quote_deadline=datetime.now(timezone.utc) + timedelta(hours=7),
            mode=LoadMode.tl, weight_lb=38200,
            dimensions=[{"pieces": 24, "length": 48, "width": 40, "height": 52}],
            commodity="Machined hydraulic assemblies", hazmat=False, refrigerated=False,
            government_relevance=True, sddc_relevance=True, gfm_relevance=True,
            notes="Three competitive quotes requested before award.",
            required_compliance_tags=["Active authority", "Cargo insurance", "SDDC/GFM readiness"],
            required_documents=["Operating authority", "Cargo insurance", "W-9"],
            priority="urgent", status=OpportunityStatus.evaluating, owner_id=user.id,
        ),
        FreightOpportunity(
            tenant_id=tenant.id, opportunity_number="OPP-2412",
            name="Urgent avionics uplift to Ramstein",
            customer_program="Aviation readiness program",
            contract_number="DEMO-FA8604-26-P-0088",
            origin={"city": "Philadelphia", "state": "PA", "postal_code": "19153"},
            destination={"city": "Frankfurt", "state": "HE", "postal_code": "60549"},
            pickup_at=datetime.now(timezone.utc) + timedelta(days=1),
            delivery_at=datetime.now(timezone.utc) + timedelta(days=3),
            quote_deadline=datetime.now(timezone.utc) + timedelta(hours=3),
            mode=LoadMode.air_freight, weight_lb=4062,
            dimensions=[{"pieces": 4, "length": 48, "width": 40, "height": 52}],
            commodity="Non-sensitive avionics components", hazmat=False, refrigerated=False,
            government_relevance=True, sddc_relevance=False, gfm_relevance=True,
            required_compliance_tags=["Air cargo security", "GFM readiness"],
            required_documents=["Cargo insurance", "W-9"],
            priority="critical", status=OpportunityStatus.sourcing, owner_id=user.id,
        ),
        FreightOpportunity(
            tenant_id=tenant.id, opportunity_number="OPP-2409",
            name="York plant LTL replenishment",
            customer_program="Susquehanna Controls",
            origin={"city": "York", "state": "PA", "postal_code": "17401"},
            destination={"city": "Charlotte", "state": "NC", "postal_code": "28202"},
            pickup_at=datetime.now(timezone.utc) + timedelta(days=5),
            delivery_at=datetime.now(timezone.utc) + timedelta(days=8),
            quote_deadline=datetime.now(timezone.utc) + timedelta(days=2),
            mode=LoadMode.ltl, weight_lb=4200,
            dimensions=[{"pieces": 6, "length": 48, "width": 40, "height": 44}],
            commodity="Industrial control valves", hazmat=False, refrigerated=False,
            required_compliance_tags=["Active authority", "Cargo insurance"],
            required_documents=["Cargo insurance"],
            priority="normal", status=OpportunityStatus.rfq_open, owner_id=user.id,
        ),
    ]
    db.add_all(opportunities)
    db.flush()

    primary = opportunities[0]
    candidate_codes = ["KFP", "SGL", "BRX", "CFL", "AOO"]
    bid_values = {"KFP": (2840, 2), "SGL": (2975, 2), "BRX": (2775, 2)}
    match_by_code = {}
    for code in candidate_codes:
        carrier = carriers[code]
        scored = score_carrier(primary, carrier)
        match = OpportunityCarrier(
            tenant_id=tenant.id, opportunity_id=primary.id, carrier_id=carrier.id,
            status=OpportunityCarrierStatus.quoted if code in bid_values else OpportunityCarrierStatus.shortlisted,
            shortlisted=code in {"KFP", "SGL", "BRX"},
            match_score=scored["score"], score_breakdown=scored["breakdown"],
            rfq_sent_at=datetime.now(timezone.utc) - timedelta(hours=4) if code in {"KFP", "SGL", "BRX"} else None,
            responded_at=datetime.now(timezone.utc) - timedelta(hours=2) if code in bid_values else None,
        )
        if match.shortlisted:
            rfq = build_rfq(primary, carrier, carrier.primary_contact_name or "Carrier Partner")
            match.rfq_subject, match.rfq_body = rfq["subject"], rfq["body"]
            match.rfq_generated_at = datetime.now(timezone.utc) - timedelta(hours=5)
        db.add(match); db.flush()
        match_by_code[code] = match
        if code in bid_values:
            amount, transit = bid_values[code]
            db.add(CarrierBid(
                tenant_id=tenant.id, opportunity_id=primary.id,
                opportunity_carrier_id=match.id, carrier_id=carrier.id,
                amount=Decimal(str(amount)), transit_days=transit,
                fuel_surcharge=Decimal("0"), carrier_contact=carrier.primary_contact_name,
                notes="Capacity confirmed; rate includes fuel and standard appointment.",
                expires_at=primary.quote_deadline + timedelta(hours=24),
                received_at=datetime.now(timezone.utc) - timedelta(hours=2),
            ))

    air = opportunities[1]
    for code in ["LAC", "SGL"]:
        carrier = carriers[code]
        scored = score_carrier(air, carrier)
        db.add(OpportunityCarrier(
            tenant_id=tenant.id, opportunity_id=air.id, carrier_id=carrier.id,
            status=OpportunityCarrierStatus.shortlisted, shortlisted=True,
            match_score=scored["score"], score_breakdown=scored["breakdown"],
        ))

    ltl = opportunities[2]
    for code in ["KFP", "BRX", "TNP"]:
        carrier = carriers[code]
        scored = score_carrier(ltl, carrier)
        match = OpportunityCarrier(
            tenant_id=tenant.id, opportunity_id=ltl.id, carrier_id=carrier.id,
            status=OpportunityCarrierStatus.rfq_sent, shortlisted=True,
            match_score=scored["score"], score_breakdown=scored["breakdown"],
            rfq_sent_at=datetime.now(timezone.utc) - timedelta(hours=9),
        )
        rfq = build_rfq(ltl, carrier, carrier.primary_contact_name or "Carrier Partner")
        match.rfq_subject, match.rfq_body = rfq["subject"], rfq["body"]
        match.rfq_generated_at = datetime.now(timezone.utc) - timedelta(hours=10)
        db.add(match)
    db.commit()


def main():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_tenant(db, "Industrial Distributor Demo", "industrial-distributor-demo", "industrial_distributor")
        seed_tenant(db, "Light Manufacturer Demo", "light-manufacturer-demo", "light_manufacturer")
        freight_tenant = seed_tenant(db, "Keystone Freight Partners Demo", "keystone-freight-demo", "hybrid_freight")
        seed_freight_data(db, freight_tenant)
        seed_procurement_data(db, freight_tenant)
    print("FlowSight demo tenants seeded. Login: maya@demo.flowsight.ai / FlowSightDemo!")


if __name__ == "__main__":
    main()
