import csv
import io
import os
import time
import uuid
from decimal import Decimal
from pathlib import Path
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import get_settings
from .database import Base, engine, get_db
from .dependencies import current_user, require_roles
from .models import (
    AuditLog, Carrier, CarrierBid, CarrierComplianceDocument, Customer, ExceptionEvent,
    ExceptionStatus, FeedbackItem, FreightAward, FreightDocument, FreightEvent,
    FreightInvoice, FreightInvoiceStatus, FreightOpportunity, FreightQuote, FreightShipment,
    FreightTender, ImportJob, ImportMapping, InvoiceLineItem, LoadMode, OpportunityCarrier,
    OpportunityCarrierStatus, OpportunityStatus, QuoteLineItem, Role, Task, TenderStatus,
    Tenant, User
)
from .schemas import (
    AwardCreate, CarrierBidCreate, CarrierCreate, ExceptionOut, FeedbackCreate,
    ForecastRequest, FreightQuoteCreate, FreightQuoteRequest, ImportMappingRequest,
    InvoiceCreate, LoginRequest, OpportunityCarrierStatusUpdate, OpportunityCreate,
    OpportunityShortlist, RFQGenerateRequest, TaskCreate, TenderCreate, TenantCreate,
    TokenResponse
)
from .security import create_access_token, hash_password, verify_password
from .services.ai import GroundedSummaryProvider
from .services.forecasting import select_forecast
from .services.freight_invoicing import invoice_analytics, validate_invoice_transition
from .services.freight_pricing import FreightQuoteInput, calculate_freight_quote, external_quote_view
from .services.imports import preview_file, validate_mapping
from .services.procurement import build_rfq, recommend_bid, score_carrier

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="FlowSight AI API",
    version="0.1.0",
    description="Multi-tenant operations intelligence and action-layer API.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

request_windows: dict[str, deque] = defaultdict(deque)
EXTERNAL_FREIGHT_ROLES = {Role.readonly_client, Role.readonly_partner}


def freight_mode(value: str) -> LoadMode:
    normalized = value.lower().replace(" ", "_")
    try:
        return LoadMode(normalized)
    except ValueError as exc:
        raise HTTPException(422, f"Unsupported freight mode: {value}") from exc


def is_external_freight_user(user: User) -> bool:
    return user.role in EXTERNAL_FREIGHT_ROLES


def tender_view(item: FreightTender, external: bool = False) -> dict:
    result = {
        "id": item.id, "tender_number": item.tender_number, "shipment_id": item.shipment_id,
        "customer_id": item.customer_id, "carrier_id": item.carrier_id, "lane_id": item.lane_id,
        "mode": item.mode.value, "status": item.status.value, "issued_at": item.issued_at,
        "expires_at": item.expires_at, "awarded_at": item.awarded_at,
        "quoted_amount": float(item.quoted_amount or 0), "client_notes": item.client_notes,
    }
    if not external:
        result.update({
            "internal_cost": float(item.internal_cost or 0),
            "target_margin_pct": item.target_margin_pct,
            "internal_notes": item.internal_notes,
            "owner_id": item.owner_id,
        })
    return result


def invoice_view(item: FreightInvoice) -> dict:
    return {
        "id": item.id, "invoice_number": item.invoice_number, "shipment_id": item.shipment_id,
        "tender_id": item.tender_id, "quote_id": item.quote_id, "customer_id": item.customer_id,
        "status": item.status.value, "issued_at": item.issued_at, "due_at": item.due_at,
        "quoted_total": float(item.quoted_total or 0), "subtotal": float(item.subtotal),
        "tax_total": float(item.tax_total), "total": float(item.total),
        "amount_paid": float(item.amount_paid), "balance_due": float(item.balance_due),
        "currency": item.currency,
    }


def carrier_view(item: Carrier, compliance: list[CarrierComplianceDocument] | None = None) -> dict:
    return {
        "id": item.id, "code": item.code, "name": item.name, "tier": item.tier,
        "classification": item.classification, "covered_modes": item.covered_modes,
        "headquarters": item.headquarters, "regions_served": item.regions_served,
        "government_business": item.government_business, "sddc_registered": item.sddc_registered,
        "gfm_approved": item.gfm_approved, "dod_relevant": item.dod_relevant,
        "website": item.website, "primary_contact_name": item.primary_contact_name,
        "primary_contact_email": item.primary_contact_email,
        "primary_contact_phone": item.primary_contact_phone, "notes": item.notes,
        "authority_status": item.authority_status,
        "insurance_expires_on": item.insurance_expires_on,
        "hazmat_capable": item.hazmat_capable,
        "refrigerated_capable": item.refrigerated_capable,
        "relationship_status": item.relationship_status,
        "compliance_status": item.compliance_status,
        "last_contacted_at": item.last_contacted_at,
        "performance_score": item.performance_score, "prior_awards": item.prior_awards,
        "compliance_documents": [{
            "id": document.id, "document_type": document.document_type,
            "status": document.status, "expires_on": document.expires_on,
            "verified_at": document.verified_at,
        } for document in (compliance or [])],
    }


def opportunity_view(item: FreightOpportunity) -> dict:
    return {
        "id": item.id, "opportunity_number": item.opportunity_number, "name": item.name,
        "customer_program": item.customer_program, "contract_number": item.contract_number,
        "origin": item.origin, "destination": item.destination, "pickup_at": item.pickup_at,
        "delivery_at": item.delivery_at, "quote_deadline": item.quote_deadline,
        "mode": item.mode.value, "weight_lb": item.weight_lb, "dimensions": item.dimensions,
        "commodity": item.commodity, "hazmat": item.hazmat, "refrigerated": item.refrigerated,
        "government_relevance": item.government_relevance,
        "sddc_relevance": item.sddc_relevance, "gfm_relevance": item.gfm_relevance,
        "notes": item.notes, "required_compliance_tags": item.required_compliance_tags,
        "required_documents": item.required_documents, "priority": item.priority,
        "status": item.status.value, "owner_id": item.owner_id,
        "awarded_carrier_id": item.awarded_carrier_id,
        "decision_rationale": item.decision_rationale, "awarded_at": item.awarded_at,
        "created_at": item.created_at,
    }


def opportunity_carrier_view(item: OpportunityCarrier, carrier: Carrier) -> dict:
    return {
        "id": item.id, "opportunity_id": item.opportunity_id, "carrier_id": item.carrier_id,
        "carrier": carrier_view(carrier), "status": item.status.value,
        "shortlisted": item.shortlisted, "match_score": item.match_score,
        "score_breakdown": item.score_breakdown, "manual_adjustment": item.manual_adjustment,
        "rfq_subject": item.rfq_subject, "rfq_body": item.rfq_body,
        "rfq_generated_at": item.rfq_generated_at, "rfq_sent_at": item.rfq_sent_at,
        "responded_at": item.responded_at,
    }


def carrier_bid_view(item: CarrierBid, carrier: Carrier | None = None) -> dict:
    return {
        "id": item.id, "opportunity_id": item.opportunity_id,
        "opportunity_carrier_id": item.opportunity_carrier_id,
        "carrier_id": item.carrier_id, "carrier_name": carrier.name if carrier else None,
        "amount": float(item.amount), "currency": item.currency,
        "transit_days": item.transit_days, "accessorials": item.accessorials,
        "fuel_surcharge": float(item.fuel_surcharge), "expires_at": item.expires_at,
        "carrier_contact": item.carrier_contact, "notes": item.notes,
        "status": item.status, "received_at": item.received_at,
    }


def opportunity_comparison(db: Session, opportunity: FreightOpportunity) -> dict:
    matches = db.scalars(
        select(OpportunityCarrier).where(
            OpportunityCarrier.opportunity_id == opportunity.id,
            OpportunityCarrier.tenant_id == opportunity.tenant_id,
        )
    ).all()
    carriers = {
        item.id: item for item in db.scalars(
            select(Carrier).where(Carrier.tenant_id == opportunity.tenant_id)
        ).all()
    }
    bids = db.scalars(
        select(CarrierBid).where(
            CarrierBid.opportunity_id == opportunity.id,
            CarrierBid.tenant_id == opportunity.tenant_id,
        ).order_by(CarrierBid.received_at.desc())
    ).all()
    match_by_carrier = {item.carrier_id: item for item in matches}
    latest_bid: dict[str, CarrierBid] = {}
    for bid in bids:
        latest_bid.setdefault(bid.carrier_id, bid)
    rows = []
    for carrier_id, bid in latest_bid.items():
        carrier = carriers.get(carrier_id)
        match = match_by_carrier.get(carrier_id)
        if not carrier or not match:
            continue
        rows.append({
            **carrier_bid_view(bid, carrier),
            "match_score": match.match_score,
            "compliance_status": carrier.compliance_status,
            "government_ready": any([
                carrier.government_business, carrier.sddc_registered,
                carrier.gfm_approved, carrier.dod_relevant,
            ]),
            "eligible": carrier.relationship_status != "do_not_use"
                and carrier.compliance_status not in {"expired", "blocked"},
            "score_breakdown": match.score_breakdown,
        })
    return {"items": rows, "recommendation": recommend_bid(rows)}


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    key = request.client.host if request.client else "unknown"
    now = time.time()
    window = request_windows[key]
    while window and window[0] < now - 60:
        window.popleft()
    if len(window) >= 180:
        return Response("Rate limit exceeded", status_code=429)
    window.append(now)
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    response.headers["x-content-type-options"] = "nosniff"
    response.headers["x-frame-options"] = "DENY"
    return response


@app.get("/health")
def health():
    return {"status": "ok", "service": "flowsight-api", "time": datetime.now(timezone.utc).isoformat()}


@app.post("/v1/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    tenant = db.scalar(select(Tenant).where(Tenant.slug == payload.tenant_slug))
    user = db.scalar(select(User).where(User.tenant_id == tenant.id, User.email == payload.email)) if tenant else None
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    return {
        "access_token": create_access_token(user.id, user.tenant_id, user.role.value),
        "user": {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role.value}
    }


@app.post("/v1/auth/register", status_code=201)
def register(payload: TenantCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Tenant).where(Tenant.slug == payload.slug)):
        raise HTTPException(status_code=409, detail="Workspace slug already exists")
    tenant = Tenant(name=payload.name, slug=payload.slug, business_type=payload.business_type)
    db.add(tenant)
    db.flush()
    user = User(
        tenant_id=tenant.id, email=payload.admin_email, full_name=payload.admin_name,
        password_hash=hash_password(payload.password), role="tenant_admin", verified=False
    )
    db.add(user)
    db.commit()
    return {"tenant_id": tenant.id, "user_id": user.id, "next": "verify_email"}


@app.get("/v1/dashboard")
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    items = db.scalars(
        select(ExceptionEvent).where(
            ExceptionEvent.tenant_id == user.tenant_id,
            ExceptionEvent.status.in_([ExceptionStatus.open, ExceptionStatus.in_progress])
        )
    ).all()
    total_impact = sum(float(x.estimated_impact) for x in items)
    return {
        "kpis": {
            "revenue_at_risk": total_impact,
            "likely_stockouts": len([x for x in items if x.exception_type == "likely_stockout"]),
            "late_pos": len([x for x in items if x.exception_type == "late_purchase_order"]),
            "service_level": 94.1,
            "forecast_accuracy": 91.8,
        },
        "priority_exceptions": [ExceptionOut.model_validate(x) for x in sorted(items, key=lambda x: x.severity_score, reverse=True)[:7]],
        "freshness": {"inventory": "8 minutes", "purchase_orders": "10 minutes", "sales_orders": "1 day"}
    }


@app.get("/v1/exceptions", response_model=list[ExceptionOut])
def list_exceptions(
    status: str | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    query = select(ExceptionEvent).where(ExceptionEvent.tenant_id == user.tenant_id)
    if status:
        query = query.where(ExceptionEvent.status == status)
    return db.scalars(query.order_by(ExceptionEvent.severity_score.desc())).all()


@app.patch("/v1/exceptions/{exception_id}")
def update_exception(
    exception_id: str, status: ExceptionStatus, usefulness: int | None = None,
    false_positive_reason: str | None = None, user: User = Depends(current_user),
    db: Session = Depends(get_db)
):
    item = db.scalar(select(ExceptionEvent).where(ExceptionEvent.id == exception_id, ExceptionEvent.tenant_id == user.tenant_id))
    if not item:
        raise HTTPException(404, "Exception not found")
    before = {"status": item.status.value, "usefulness": item.usefulness}
    item.status, item.usefulness, item.false_positive_reason = status, usefulness, false_positive_reason
    db.add(AuditLog(tenant_id=user.tenant_id, actor_user_id=user.id, action="exception.updated", entity_type="exception", entity_id=item.id, before=before, after={"status": status.value, "usefulness": usefulness}))
    db.commit()
    return {"id": item.id, "status": item.status}


@app.post("/v1/tasks", status_code=201)
def create_task(payload: TaskCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if payload.exception_id:
        exception = db.scalar(select(ExceptionEvent).where(ExceptionEvent.id == payload.exception_id, ExceptionEvent.tenant_id == user.tenant_id))
        if not exception:
            raise HTTPException(404, "Linked exception not found")
        exception.status = ExceptionStatus.in_progress
    task = Task(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(task)
    db.add(AuditLog(tenant_id=user.tenant_id, actor_user_id=user.id, action="task.created", entity_type="task", entity_id=task.id, after=payload.model_dump(mode="json")))
    db.commit()
    return {"id": task.id, "status": task.status}


@app.get("/v1/tasks")
def list_tasks(user: User = Depends(current_user), db: Session = Depends(get_db)):
    tasks = db.scalars(select(Task).where(Task.tenant_id == user.tenant_id, Task.deleted_at.is_(None))).all()
    return [{"id": t.id, "title": t.title, "status": t.status, "priority": t.priority, "due_at": t.due_at} for t in tasks]


@app.post("/v1/forecasts/run")
def run_forecast(payload: ForecastRequest, user: User = Depends(current_user)):
    result = select_forecast(payload.values, payload.horizon)
    return {"tenant_id": user.tenant_id, **result}


@app.post("/v1/imports/preview")
async def import_preview(
    file: UploadFile = File(...), user: User = Depends(current_user),
):
    if not file.filename or not file.filename.lower().endswith((".csv", ".xlsx")):
        raise HTTPException(415, "Only CSV and XLSX files are supported")
    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(413, "File exceeds 25 MB")
    return preview_file(file.filename, content)


@app.post("/v1/imports/validate-mapping")
def mapping_validation(payload: ImportMappingRequest, user: User = Depends(current_user)):
    return validate_mapping(payload.entity_type, payload.mapping)


@app.post("/v1/imports", status_code=202)
async def create_import(
    entity_type: str, file: UploadFile = File(...), mapping_id: str | None = None,
    user: User = Depends(current_user), db: Session = Depends(get_db)
):
    content = await file.read()
    preview = preview_file(file.filename or "upload.csv", content)
    job = ImportJob(
        tenant_id=user.tenant_id, entity_type=entity_type, filename=file.filename or "upload",
        storage_key=f"{user.tenant_id}/imports/{uuid.uuid4()}/{file.filename}", mapping_id=mapping_id,
        status="validated", row_count=len(preview["rows"]), detected_metadata=preview["detected"]
    )
    db.add(job)
    db.commit()
    return {"job_id": job.id, "status": job.status, "preview": preview}


@app.post("/v1/feedback", status_code=201)
def create_feedback(payload: FeedbackCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = FeedbackItem(tenant_id=user.tenant_id, user_id=user.id, **payload.model_dump())
    db.add(item)
    db.commit()
    return {"id": item.id, "status": item.status}


@app.get("/v1/ai/daily-brief")
def daily_brief(user: User = Depends(current_user), db: Session = Depends(get_db)):
    items = db.scalars(select(ExceptionEvent).where(ExceptionEvent.tenant_id == user.tenant_id)).all()
    evidence = [{
        "id": x.id, "title": x.title, "status": x.status.value, "severity_score": x.severity_score,
        "estimated_impact": float(x.estimated_impact), "recommended_action": x.recommended_action
    } for x in items]
    return GroundedSummaryProvider().daily_brief(evidence, {})


@app.get("/v1/reports/executive.pdf")
def executive_report(user: User = Depends(current_user), db: Session = Depends(get_db)):
    tenant = db.get(Tenant, user.tenant_id)
    items = db.scalars(select(ExceptionEvent).where(ExceptionEvent.tenant_id == user.tenant_id).order_by(ExceptionEvent.severity_score.desc()).limit(10)).all()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"{tenant.name} - Executive Operations Brief", styles["Title"]),
        Paragraph(datetime.now(timezone.utc).strftime("%B %d, %Y"), styles["Normal"]), Spacer(1, 18),
        Paragraph(f"Top operating risks represent ${sum(float(x.estimated_impact) for x in items):,.0f} in estimated impact.", styles["Heading2"]), Spacer(1, 10)
    ]
    data = [["Risk", "Severity", "Confidence", "Impact"]] + [[x.title, x.severity, f"{x.confidence_score:.0f}%", f"${float(x.estimated_impact):,.0f}"] for x in items]
    table = Table(data, colWidths=[290, 65, 70, 75], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor(tenant.brand_color)),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), .4, colors.HexColor("#dfe7e5")), ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("FONTSIZE", (0,0), (-1,-1), 8), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f4f8f7")]),
        ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7),
    ]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=flowsight-executive-brief.pdf"})


@app.get("/v1/exports/exceptions.csv")
def exception_csv(user: User = Depends(current_user), db: Session = Depends(get_db)):
    items = db.scalars(select(ExceptionEvent).where(ExceptionEvent.tenant_id == user.tenant_id)).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["code", "type", "title", "severity", "confidence", "estimated_impact", "status"])
    for x in items:
        writer.writerow([x.code, x.exception_type, x.title, x.severity, x.confidence_score, x.estimated_impact, x.status.value])
    return Response(output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=exceptions.csv"})


@app.post("/v1/ingest/{entity_type}", status_code=202)
def api_ingest(
    entity_type: str, records: list[dict], x_tenant_api_key: str = Header(),
    db: Session = Depends(get_db)
):
    tenant = db.scalar(select(Tenant).where(Tenant.config["api_key"].as_string() == x_tenant_api_key))
    if not tenant:
        raise HTTPException(401, "Invalid tenant API key")
    return {"accepted": len(records), "entity_type": entity_type, "tenant_id": tenant.id, "status": "queued"}


@app.get("/v1/admin/tenants")
def admin_tenants(
    user: User = Depends(require_roles("platform_super_admin")),
    db: Session = Depends(get_db)
):
    return [{"id": t.id, "name": t.name, "plan": t.plan.value, "is_demo": t.is_demo} for t in db.scalars(select(Tenant)).all()]


@app.get("/v1/freight/carriers")
def freight_carriers(
    mode: str | None = None,
    relationship: str | None = None,
    compliance: str | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user):
        raise HTTPException(403, "Carrier intelligence is restricted to internal roles")
    query = select(Carrier).where(Carrier.tenant_id == user.tenant_id, Carrier.active.is_(True))
    if relationship:
        query = query.where(Carrier.relationship_status == relationship)
    if compliance:
        query = query.where(Carrier.compliance_status == compliance)
    items = db.scalars(query.order_by(Carrier.name)).all()
    if mode:
        normalized = freight_mode(mode).value
        items = [item for item in items if normalized in (item.covered_modes or [])]
    documents = db.scalars(
        select(CarrierComplianceDocument).where(CarrierComplianceDocument.tenant_id == user.tenant_id)
    ).all()
    docs_by_carrier: dict[str, list[CarrierComplianceDocument]] = defaultdict(list)
    for document in documents:
        docs_by_carrier[document.carrier_id].append(document)
    return [carrier_view(item, docs_by_carrier[item.id]) for item in items]


@app.post("/v1/freight/carriers", status_code=201)
def create_freight_carrier(
    payload: CarrierCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user):
        raise HTTPException(403, "Internal role required")
    if db.scalar(select(Carrier).where(Carrier.tenant_id == user.tenant_id, Carrier.code == payload.code)):
        raise HTTPException(409, "Carrier code already exists")
    item = Carrier(tenant_id=user.tenant_id, **payload.model_dump())
    item.covered_modes = [freight_mode(mode).value for mode in payload.covered_modes]
    db.add(item)
    db.add(AuditLog(
        tenant_id=user.tenant_id, actor_user_id=user.id, action="freight.carrier.created",
        entity_type="carrier", entity_id=item.id, after=payload.model_dump(mode="json"),
    ))
    db.commit()
    return carrier_view(item)


@app.get("/v1/freight/opportunities")
def list_freight_opportunities(
    status: OpportunityStatus | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user):
        raise HTTPException(403, "Procurement workspace is restricted to internal roles")
    query = select(FreightOpportunity).where(FreightOpportunity.tenant_id == user.tenant_id)
    if status:
        query = query.where(FreightOpportunity.status == status)
    items = db.scalars(query.order_by(FreightOpportunity.created_at.desc())).all()
    matches = db.scalars(
        select(OpportunityCarrier).where(OpportunityCarrier.tenant_id == user.tenant_id)
    ).all()
    bids = db.scalars(select(CarrierBid).where(CarrierBid.tenant_id == user.tenant_id)).all()
    return [{
        **opportunity_view(item),
        "matched_carriers": len([row for row in matches if row.opportunity_id == item.id]),
        "shortlisted_carriers": len([row for row in matches if row.opportunity_id == item.id and row.shortlisted]),
        "rfqs_sent": len([row for row in matches if row.opportunity_id == item.id and row.rfq_sent_at]),
        "quotes_received": len([row for row in bids if row.opportunity_id == item.id]),
    } for item in items]


@app.post("/v1/freight/opportunities", status_code=201)
def create_freight_opportunity(
    payload: OpportunityCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user):
        raise HTTPException(403, "Internal role required")
    item = FreightOpportunity(
        tenant_id=user.tenant_id,
        opportunity_number=f"OPP-{datetime.now(timezone.utc).strftime('%y%m%d')}-{uuid.uuid4().hex[:5].upper()}",
        owner_id=user.id, status=OpportunityStatus.draft,
        mode=freight_mode(payload.mode),
        **payload.model_dump(exclude={"mode"}),
    )
    db.add(item)
    db.flush()
    db.add(FreightEvent(
        tenant_id=user.tenant_id, entity_type="opportunity", entity_id=item.id,
        event_type="opportunity.created", actor_user_id=user.id,
        payload={"opportunity_number": item.opportunity_number}, external_visible=False,
    ))
    db.add(AuditLog(
        tenant_id=user.tenant_id, actor_user_id=user.id,
        action="freight.opportunity.created", entity_type="freight_opportunity",
        entity_id=item.id, after=payload.model_dump(mode="json"),
    ))
    db.commit()
    return opportunity_view(item)


@app.get("/v1/freight/opportunities/{opportunity_id}")
def get_freight_opportunity(
    opportunity_id: str,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user):
        raise HTTPException(403, "Procurement workspace is restricted to internal roles")
    item = db.scalar(select(FreightOpportunity).where(
        FreightOpportunity.id == opportunity_id, FreightOpportunity.tenant_id == user.tenant_id
    ))
    if not item:
        raise HTTPException(404, "Opportunity not found")
    carriers = {
        row.id: row for row in db.scalars(select(Carrier).where(Carrier.tenant_id == user.tenant_id)).all()
    }
    matches = db.scalars(select(OpportunityCarrier).where(
        OpportunityCarrier.opportunity_id == item.id,
        OpportunityCarrier.tenant_id == user.tenant_id,
    ).order_by(OpportunityCarrier.match_score.desc())).all()
    award = db.scalar(select(FreightAward).where(
        FreightAward.opportunity_id == item.id, FreightAward.tenant_id == user.tenant_id
    ))
    comparison = opportunity_comparison(db, item)
    return {
        **opportunity_view(item),
        "matched_carriers": [
            opportunity_carrier_view(match, carriers[match.carrier_id])
            for match in matches if match.carrier_id in carriers
        ],
        "comparison": comparison,
        "award": {
            "id": award.id, "carrier_id": award.carrier_id, "bid_id": award.bid_id,
            "amount": float(award.amount), "rationale": award.rationale,
            "awarded_at": award.awarded_at,
        } if award else None,
    }


@app.post("/v1/freight/opportunities/{opportunity_id}/match")
def match_freight_opportunity(
    opportunity_id: str,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user):
        raise HTTPException(403, "Internal role required")
    opportunity = db.scalar(select(FreightOpportunity).where(
        FreightOpportunity.id == opportunity_id, FreightOpportunity.tenant_id == user.tenant_id
    ))
    if not opportunity:
        raise HTTPException(404, "Opportunity not found")
    carriers = db.scalars(select(Carrier).where(
        Carrier.tenant_id == user.tenant_id, Carrier.active.is_(True)
    )).all()
    results = []
    for carrier in carriers:
        existing = db.scalar(select(OpportunityCarrier).where(
            OpportunityCarrier.opportunity_id == opportunity.id,
            OpportunityCarrier.carrier_id == carrier.id,
        ))
        manual_adjustment = existing.manual_adjustment if existing else 0
        scored = score_carrier(opportunity, carrier, manual_adjustment)
        match = existing or OpportunityCarrier(
            tenant_id=user.tenant_id, opportunity_id=opportunity.id, carrier_id=carrier.id
        )
        match.match_score = scored["score"]
        match.score_breakdown = scored["breakdown"]
        if not existing:
            db.add(match)
        results.append((match, carrier, scored["eligible"]))
    opportunity.status = OpportunityStatus.sourcing
    db.add(FreightEvent(
        tenant_id=user.tenant_id, entity_type="opportunity", entity_id=opportunity.id,
        event_type="opportunity.carriers_matched", actor_user_id=user.id,
        payload={"carrier_count": len(results)}, external_visible=False,
    ))
    db.commit()
    return sorted([
        {**opportunity_carrier_view(match, carrier), "eligible": eligible}
        for match, carrier, eligible in results
    ], key=lambda row: row["match_score"], reverse=True)


@app.post("/v1/freight/opportunities/{opportunity_id}/shortlist")
def shortlist_opportunity_carriers(
    opportunity_id: str,
    payload: OpportunityShortlist,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user):
        raise HTTPException(403, "Internal role required")
    opportunity = db.scalar(select(FreightOpportunity).where(
        FreightOpportunity.id == opportunity_id, FreightOpportunity.tenant_id == user.tenant_id
    ))
    if not opportunity:
        raise HTTPException(404, "Opportunity not found")
    matches = db.scalars(select(OpportunityCarrier).where(
        OpportunityCarrier.opportunity_id == opportunity.id,
        OpportunityCarrier.tenant_id == user.tenant_id,
    )).all()
    by_carrier = {item.carrier_id: item for item in matches}
    missing = [carrier_id for carrier_id in payload.carrier_ids if carrier_id not in by_carrier]
    if missing:
        raise HTTPException(422, "Run carrier matching before shortlisting")
    for match in matches:
        match.shortlisted = match.carrier_id in payload.carrier_ids
        if match.shortlisted and match.status == OpportunityCarrierStatus.not_contacted:
            match.status = OpportunityCarrierStatus.shortlisted
    db.commit()
    return {"opportunity_id": opportunity.id, "shortlisted_carrier_ids": payload.carrier_ids}


@app.post("/v1/freight/opportunities/{opportunity_id}/rfqs/generate")
def generate_opportunity_rfqs(
    opportunity_id: str,
    payload: RFQGenerateRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user):
        raise HTTPException(403, "Internal role required")
    opportunity = db.scalar(select(FreightOpportunity).where(
        FreightOpportunity.id == opportunity_id, FreightOpportunity.tenant_id == user.tenant_id
    ))
    if not opportunity:
        raise HTTPException(404, "Opportunity not found")
    query = select(OpportunityCarrier).where(
        OpportunityCarrier.opportunity_id == opportunity.id,
        OpportunityCarrier.tenant_id == user.tenant_id,
    )
    matches = db.scalars(query).all()
    selected = [
        match for match in matches
        if match.carrier_id in payload.carrier_ids
        or (not payload.carrier_ids and match.shortlisted)
    ]
    if not selected:
        raise HTTPException(422, "Shortlist at least one carrier before generating RFQs")
    carriers = {
        item.id: item for item in db.scalars(select(Carrier).where(
            Carrier.tenant_id == user.tenant_id,
            Carrier.id.in_([match.carrier_id for match in selected]),
        )).all()
    }
    generated = []
    now = datetime.now(timezone.utc)
    for match in selected:
        carrier = carriers.get(match.carrier_id)
        if not carrier:
            continue
        rfq = build_rfq(opportunity, carrier, carrier.primary_contact_name or "Carrier Partner")
        match.shortlisted = True
        match.status = OpportunityCarrierStatus.shortlisted
        match.rfq_subject = rfq["subject"]
        match.rfq_body = rfq["body"]
        match.rfq_generated_at = now
        generated.append({"opportunity_carrier_id": match.id, **rfq})
    opportunity.status = OpportunityStatus.rfq_open
    db.commit()
    return {"opportunity_id": opportunity.id, "rfqs": generated}


@app.patch("/v1/freight/opportunity-carriers/{match_id}/status")
def update_opportunity_carrier_status(
    match_id: str,
    payload: OpportunityCarrierStatusUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user):
        raise HTTPException(403, "Internal role required")
    match = db.scalar(select(OpportunityCarrier).where(
        OpportunityCarrier.id == match_id, OpportunityCarrier.tenant_id == user.tenant_id
    ))
    if not match:
        raise HTTPException(404, "Opportunity carrier not found")
    try:
        status = OpportunityCarrierStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(422, "Unsupported RFQ status") from exc
    now = datetime.now(timezone.utc)
    match.status = status
    if status == OpportunityCarrierStatus.rfq_sent:
        match.rfq_sent_at = now
    if status in {
        OpportunityCarrierStatus.responded, OpportunityCarrierStatus.quoted,
        OpportunityCarrierStatus.no_bid,
    }:
        match.responded_at = now
    carrier = db.get(Carrier, match.carrier_id)
    if carrier and status == OpportunityCarrierStatus.rfq_sent:
        carrier.last_contacted_at = now
    db.commit()
    return opportunity_carrier_view(match, carrier)


@app.post("/v1/freight/opportunities/{opportunity_id}/bids", status_code=201)
def create_carrier_bid(
    opportunity_id: str,
    payload: CarrierBidCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user):
        raise HTTPException(403, "Internal role required")
    opportunity = db.scalar(select(FreightOpportunity).where(
        FreightOpportunity.id == opportunity_id, FreightOpportunity.tenant_id == user.tenant_id
    ))
    if not opportunity:
        raise HTTPException(404, "Opportunity not found")
    match = db.scalar(select(OpportunityCarrier).where(
        OpportunityCarrier.opportunity_id == opportunity.id,
        OpportunityCarrier.carrier_id == payload.carrier_id,
        OpportunityCarrier.tenant_id == user.tenant_id,
    ))
    if not match:
        raise HTTPException(422, "Carrier must be matched to this opportunity")
    bid = CarrierBid(
        tenant_id=user.tenant_id, opportunity_id=opportunity.id,
        opportunity_carrier_id=match.id, carrier_id=payload.carrier_id,
        amount=Decimal(str(payload.amount)), currency=payload.currency.upper(),
        transit_days=payload.transit_days, accessorials=payload.accessorials,
        fuel_surcharge=Decimal(str(payload.fuel_surcharge)),
        expires_at=payload.expires_at, carrier_contact=payload.carrier_contact,
        notes=payload.notes, status=payload.status,
    )
    db.add(bid)
    match.status = OpportunityCarrierStatus.quoted
    match.responded_at = datetime.now(timezone.utc)
    opportunity.status = OpportunityStatus.evaluating
    db.flush()
    db.add(FreightEvent(
        tenant_id=user.tenant_id, entity_type="opportunity", entity_id=opportunity.id,
        event_type="opportunity.bid_received", actor_user_id=user.id,
        payload={"carrier_id": payload.carrier_id, "amount": payload.amount}, external_visible=False,
    ))
    db.commit()
    carrier = db.get(Carrier, payload.carrier_id)
    return carrier_bid_view(bid, carrier)


@app.get("/v1/freight/opportunities/{opportunity_id}/comparison")
def compare_opportunity_bids(
    opportunity_id: str,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user):
        raise HTTPException(403, "Internal role required")
    opportunity = db.scalar(select(FreightOpportunity).where(
        FreightOpportunity.id == opportunity_id, FreightOpportunity.tenant_id == user.tenant_id
    ))
    if not opportunity:
        raise HTTPException(404, "Opportunity not found")
    return opportunity_comparison(db, opportunity)


@app.post("/v1/freight/opportunities/{opportunity_id}/award", status_code=201)
def award_freight_opportunity(
    opportunity_id: str,
    payload: AwardCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user):
        raise HTTPException(403, "Internal role required")
    opportunity = db.scalar(select(FreightOpportunity).where(
        FreightOpportunity.id == opportunity_id, FreightOpportunity.tenant_id == user.tenant_id
    ))
    if not opportunity:
        raise HTTPException(404, "Opportunity not found")
    if db.scalar(select(FreightAward).where(FreightAward.opportunity_id == opportunity.id)):
        raise HTTPException(409, "Opportunity is already awarded")
    carrier = db.scalar(select(Carrier).where(
        Carrier.id == payload.carrier_id, Carrier.tenant_id == user.tenant_id
    ))
    if not carrier:
        raise HTTPException(404, "Carrier not found")
    bid = db.scalar(select(CarrierBid).where(
        CarrierBid.id == payload.bid_id, CarrierBid.opportunity_id == opportunity.id
    )) if payload.bid_id else db.scalar(select(CarrierBid).where(
        CarrierBid.carrier_id == carrier.id, CarrierBid.opportunity_id == opportunity.id
    ).order_by(CarrierBid.received_at.desc()))
    if not bid:
        raise HTTPException(422, "An award requires a recorded carrier bid")
    comparison = opportunity_comparison(db, opportunity)
    recommendation = comparison.get("recommendation") or {}
    score_snapshot = {
        key: recommendation[key]
        for key in ["carrier_id", "carrier_name", "bid_id", "amount", "comparison_score", "explanation", "evaluated_at"]
        if key in recommendation
    }
    award = FreightAward(
        tenant_id=user.tenant_id, opportunity_id=opportunity.id, carrier_id=carrier.id,
        bid_id=bid.id, awarded_by_id=user.id, amount=bid.amount,
        rationale=payload.rationale,
        score_snapshot=score_snapshot,
    )
    db.add(award)
    opportunity.status = OpportunityStatus.awarded
    opportunity.awarded_carrier_id = carrier.id
    opportunity.decision_rationale = payload.rationale
    opportunity.awarded_at = datetime.now(timezone.utc)
    matches = db.scalars(select(OpportunityCarrier).where(
        OpportunityCarrier.opportunity_id == opportunity.id
    )).all()
    for match in matches:
        match.status = (
            OpportunityCarrierStatus.awarded
            if match.carrier_id == carrier.id
            else OpportunityCarrierStatus.rejected
        )
    carrier.prior_awards += 1
    db.flush()
    db.add(FreightEvent(
        tenant_id=user.tenant_id, entity_type="opportunity", entity_id=opportunity.id,
        event_type="opportunity.awarded", actor_user_id=user.id,
        payload={"carrier_id": carrier.id, "bid_id": bid.id, "amount": float(bid.amount)},
        external_visible=False,
    ))
    db.add(AuditLog(
        tenant_id=user.tenant_id, actor_user_id=user.id,
        action="freight.opportunity.awarded", entity_type="freight_opportunity",
        entity_id=opportunity.id, after={
            "carrier_id": carrier.id, "bid_id": bid.id,
            "amount": float(bid.amount), "rationale": payload.rationale,
        },
    ))
    db.commit()
    return {
        "id": award.id, "opportunity_id": opportunity.id, "carrier_id": carrier.id,
        "carrier_name": carrier.name, "bid_id": bid.id, "amount": float(award.amount),
        "rationale": award.rationale, "awarded_at": award.awarded_at,
    }


@app.get("/v1/freight/opportunities/{opportunity_id}/procurement-summary.md")
def export_procurement_summary(
    opportunity_id: str,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user):
        raise HTTPException(403, "Internal role required")
    opportunity = db.scalar(select(FreightOpportunity).where(
        FreightOpportunity.id == opportunity_id, FreightOpportunity.tenant_id == user.tenant_id
    ))
    if not opportunity:
        raise HTTPException(404, "Opportunity not found")
    comparison = opportunity_comparison(db, opportunity)
    matches = db.scalars(select(OpportunityCarrier).where(
        OpportunityCarrier.opportunity_id == opportunity.id
    )).all()
    carrier_names = {
        carrier.id: carrier.name for carrier in db.scalars(select(Carrier).where(
            Carrier.tenant_id == user.tenant_id
        )).all()
    }
    award = db.scalar(select(FreightAward).where(FreightAward.opportunity_id == opportunity.id))
    lines = [
        f"# Procurement Summary — {opportunity.opportunity_number}",
        "", f"**Opportunity:** {opportunity.name}",
        f"**Program / contract:** {opportunity.customer_program or 'N/A'} / {opportunity.contract_number or 'N/A'}",
        f"**Lane:** {opportunity.origin.get('city')}, {opportunity.origin.get('state')} → {opportunity.destination.get('city')}, {opportunity.destination.get('state')}",
        f"**Mode:** {opportunity.mode.value.replace('_', ' ').title()}",
        f"**Pickup:** {opportunity.pickup_at.isoformat()}",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        "", "## Procurement activity",
        f"- Carriers considered: {len(matches)}",
        f"- Carriers shortlisted: {len([item for item in matches if item.shortlisted])}",
        f"- RFQs sent: {len([item for item in matches if item.rfq_sent_at])}",
        f"- Quotes received: {len(comparison['items'])}",
        "", "## Bid comparison",
        "", "| Carrier | Rate | Transit | Fit score | Compliance |",
        "|---|---:|---:|---:|---|",
    ]
    for row in comparison["items"]:
        lines.append(
            f"| {row['carrier_name']} | ${row['amount']:,.2f} | {row.get('transit_days') or 'N/A'} days | "
            f"{row.get('match_score', 0):.0f}/100 | {row.get('compliance_status', 'unknown')} |"
        )
    lines.extend([
        "", "## Recommendation",
        comparison["recommendation"]["explanation"] if comparison["recommendation"] else "No eligible bid recommendation is available.",
        "", "## Award decision",
        f"**Awarded carrier:** {carrier_names.get(award.carrier_id, 'N/A') if award else 'Not awarded'}",
        f"**Awarded rate:** ${float(award.amount):,.2f}" if award else "**Awarded rate:** N/A",
        f"**Decision rationale:** {award.rationale}" if award else "**Decision rationale:** Pending",
    ])
    content = "\n".join(lines)
    filename = f"{opportunity.opportunity_number.lower()}-procurement-summary.md"
    return Response(content, media_type="text/markdown", headers={
        "Content-Disposition": f'attachment; filename="{filename}"'
    })


@app.get("/v1/freight/dashboard")
def freight_dashboard(
    workspace: str = "internal",
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    external = workspace == "client" or is_external_freight_user(user)
    tenders = db.scalars(select(FreightTender).where(FreightTender.tenant_id == user.tenant_id)).all()
    quotes = db.scalars(select(FreightQuote).where(FreightQuote.tenant_id == user.tenant_id)).all()
    invoices = db.scalars(select(FreightInvoice).where(FreightInvoice.tenant_id == user.tenant_id)).all()
    shipments = db.scalars(select(FreightShipment).where(FreightShipment.tenant_id == user.tenant_id)).all()
    opportunities = db.scalars(select(FreightOpportunity).where(FreightOpportunity.tenant_id == user.tenant_id)).all()
    opportunity_carriers = db.scalars(select(OpportunityCarrier).where(OpportunityCarrier.tenant_id == user.tenant_id)).all()
    carrier_bids = db.scalars(select(CarrierBid).where(CarrierBid.tenant_id == user.tenant_id)).all()
    carriers = db.scalars(select(Carrier).where(Carrier.tenant_id == user.tenant_id, Carrier.active.is_(True))).all()
    awards = db.scalars(select(FreightAward).where(FreightAward.tenant_id == user.tenant_id)).all()
    invoice_rows = [invoice_view(item) for item in invoices]
    quoted_total = sum(float(item.client_total) for item in quotes)
    internal_cost = sum(float(item.internal_cost) for item in quotes)
    dashboard = {
        "workspace": "client" if external else "internal",
        "loads": len(shipments),
        "active_tenders": len([x for x in tenders if x.status not in {TenderStatus.closed, TenderStatus.rejected, TenderStatus.expired}]),
        "quote_turnaround_minutes": 18,
        "tender_acceptance_rate": round(100 * len([x for x in tenders if x.status in {TenderStatus.accepted, TenderStatus.awarded, TenderStatus.in_transit, TenderStatus.delivered, TenderStatus.invoiced, TenderStatus.paid}]) / len(tenders), 2) if tenders else 0,
        "client_spend_or_revenue": round(quoted_total, 2),
        "invoice_summary": invoice_analytics(invoice_rows),
        "mode_mix": {
            mode.value: len([x for x in shipments if x.mode == mode])
            for mode in LoadMode
        },
        "procurement": {
            "open_opportunities": len([x for x in opportunities if x.status not in {OpportunityStatus.awarded, OpportunityStatus.closed, OpportunityStatus.canceled}]),
            "rfqs_sent": len([x for x in opportunity_carriers if x.rfq_sent_at]),
            "quotes_received": len(carrier_bids),
            "quote_response_rate": round(
                100 * len([x for x in opportunity_carriers if x.status in {
                    OpportunityCarrierStatus.responded, OpportunityCarrierStatus.quoted,
                    OpportunityCarrierStatus.awarded, OpportunityCarrierStatus.no_bid
                }]) / len([x for x in opportunity_carriers if x.rfq_sent_at]), 1
            ) if any(x.rfq_sent_at for x in opportunity_carriers) else 0,
            "awarded_opportunities": len(awards),
            "carriers_missing_poc": len([x for x in carriers if not x.primary_contact_email]),
            "carriers_missing_compliance": len([x for x in carriers if x.compliance_status != "complete"]),
        },
    }
    if not external:
        dashboard["internal_cost"] = round(internal_cost, 2)
        dashboard["gross_margin"] = round(quoted_total - internal_cost, 2)
        dashboard["gross_margin_pct"] = round(100 * (quoted_total - internal_cost) / quoted_total, 2) if quoted_total else 0
    return dashboard


@app.get("/v1/freight/tenders")
def freight_tenders(
    workspace: str = "internal",
    status: str | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    query = select(FreightTender).where(FreightTender.tenant_id == user.tenant_id)
    if status:
        query = query.where(FreightTender.status == status)
    external = workspace == "client" or is_external_freight_user(user)
    return [tender_view(item, external) for item in db.scalars(query.order_by(FreightTender.created_at.desc())).all()]


@app.post("/v1/freight/tenders", status_code=201)
def create_freight_tender(
    payload: TenderCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user):
        raise HTTPException(403, "Client and partner roles cannot create internal tenders")
    item = FreightTender(
        tenant_id=user.tenant_id,
        tender_number=f"TND-{datetime.now(timezone.utc).strftime('%y%m%d%H%M%S')}",
        mode=freight_mode(payload.mode),
        status=TenderStatus.draft,
        owner_id=user.id,
        **payload.model_dump(exclude={"mode"})
    )
    db.add(item)
    db.flush()
    db.add(FreightEvent(
        tenant_id=user.tenant_id, entity_type="tender", entity_id=item.id,
        event_type="tender.created", actor_user_id=user.id,
        payload={"tender_number": item.tender_number}, external_visible=True
    ))
    db.add(AuditLog(
        tenant_id=user.tenant_id, actor_user_id=user.id, action="freight.tender.created",
        entity_type="freight_tender", entity_id=item.id, after=payload.model_dump(mode="json")
    ))
    db.commit()
    return tender_view(item)


@app.patch("/v1/freight/tenders/{tender_id}/status")
def change_tender_status(
    tender_id: str,
    status: TenderStatus,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user) and status not in {TenderStatus.accepted, TenderStatus.rejected}:
        raise HTTPException(403, "Client roles may only accept or reject a tender")
    item = db.scalar(select(FreightTender).where(FreightTender.id == tender_id, FreightTender.tenant_id == user.tenant_id))
    if not item:
        raise HTTPException(404, "Tender not found")
    before = item.status.value
    item.status = status
    db.add(FreightEvent(
        tenant_id=user.tenant_id, entity_type="tender", entity_id=item.id,
        event_type=f"tender.{status.value}", actor_user_id=user.id,
        payload={"from": before, "to": status.value}, external_visible=True
    ))
    db.commit()
    return tender_view(item, is_external_freight_user(user))


@app.post("/v1/freight/quotes/calculate")
def calculate_quote(payload: FreightQuoteRequest, user: User = Depends(current_user)):
    request = FreightQuoteInput(**payload.model_dump(exclude={"workspace"}))
    try:
        result = calculate_freight_quote(request)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return external_quote_view(result) if payload.workspace == "client" or is_external_freight_user(user) else result


@app.post("/v1/freight/quotes", status_code=201)
def create_quote(
    payload: FreightQuoteCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if is_external_freight_user(user):
        raise HTTPException(403, "Client roles may request rates but cannot create carrier-side quotes")
    request = FreightQuoteInput(**payload.model_dump(exclude={"workspace", "tender_id"}))
    result = calculate_freight_quote(request)
    quote = FreightQuote(
        tenant_id=user.tenant_id,
        quote_number=f"Q-{datetime.now(timezone.utc).strftime('%y%m%d%H%M%S')}",
        tender_id=payload.tender_id,
        customer_id=payload.customer_id,
        carrier_id=payload.carrier_id,
        mode=freight_mode(payload.mode),
        status="approval_required" if result["requires_approval"] else "ready",
        internal_cost=Decimal(str(result["internal_cost"])),
        client_total=Decimal(str(result["client_total"])),
        margin_amount=Decimal(str(result["margin_amount"])),
        margin_pct=result["margin_pct"],
        requires_approval=result["requires_approval"],
        calculation_input=payload.model_dump(mode="json"),
        calculation_trace=result["calculation_trace"],
        explanation=result["explanation"],
    )
    db.add(quote)
    db.flush()
    for line in result["line_items"]:
        db.add(QuoteLineItem(
            tenant_id=user.tenant_id, quote_id=quote.id, code=line["code"],
            description=line["description"], amount=Decimal(str(line["amount"])),
            quantity=1, unit_rate=Decimal(str(line["amount"]))
        ))
    db.add(FreightEvent(
        tenant_id=user.tenant_id, entity_type="quote", entity_id=quote.id,
        event_type="quote.created", actor_user_id=user.id,
        payload={"quote_number": quote.quote_number, "requires_approval": quote.requires_approval},
        external_visible=False
    ))
    db.commit()
    return {"id": quote.id, "quote_number": quote.quote_number, **result}


@app.get("/v1/freight/invoices")
def freight_invoice_list(user: User = Depends(current_user), db: Session = Depends(get_db)):
    items = db.scalars(
        select(FreightInvoice).where(FreightInvoice.tenant_id == user.tenant_id).order_by(FreightInvoice.created_at.desc())
    ).all()
    rows = [invoice_view(item) for item in items]
    return {"items": rows, "analytics": invoice_analytics(rows)}


@app.post("/v1/freight/invoices", status_code=201)
def create_freight_invoice(
    payload: InvoiceCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if user.role not in {Role.platform_admin, Role.tenant_admin, Role.operations, Role.billing_finance}:
        raise HTTPException(403, "Billing role required")
    subtotal = sum(Decimal(str(line.get("amount", 0))) for line in payload.line_items)
    invoice = FreightInvoice(
        tenant_id=user.tenant_id,
        invoice_number=f"INV-{datetime.now(timezone.utc).strftime('%y%m%d%H%M%S')}",
        shipment_id=payload.shipment_id, tender_id=payload.tender_id, quote_id=payload.quote_id,
        customer_id=payload.customer_id, status=FreightInvoiceStatus.draft,
        due_at=payload.due_at, quoted_total=Decimal(str(payload.quoted_total or 0)),
        subtotal=subtotal, total=subtotal, balance_due=subtotal,
    )
    db.add(invoice)
    db.flush()
    for line in payload.line_items:
        amount = Decimal(str(line.get("amount", 0)))
        db.add(InvoiceLineItem(
            tenant_id=user.tenant_id, invoice_id=invoice.id,
            code=str(line.get("code", "FREIGHT")), description=str(line.get("description", "Freight charge")),
            quantity=float(line.get("quantity", 1)), unit_rate=Decimal(str(line.get("unit_rate", amount))),
            amount=amount
        ))
    db.add(FreightEvent(
        tenant_id=user.tenant_id, entity_type="invoice", entity_id=invoice.id,
        event_type="invoice.created", actor_user_id=user.id,
        payload={"invoice_number": invoice.invoice_number}, external_visible=True
    ))
    db.commit()
    return invoice_view(invoice)


@app.patch("/v1/freight/invoices/{invoice_id}/status")
def update_freight_invoice_status(
    invoice_id: str,
    status: FreightInvoiceStatus,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if user.role not in {Role.platform_admin, Role.tenant_admin, Role.operations, Role.billing_finance}:
        raise HTTPException(403, "Billing role required")
    item = db.scalar(select(FreightInvoice).where(FreightInvoice.id == invoice_id, FreightInvoice.tenant_id == user.tenant_id))
    if not item:
        raise HTTPException(404, "Invoice not found")
    if not validate_invoice_transition(item.status.value, status.value):
        raise HTTPException(409, f"Cannot transition invoice from {item.status.value} to {status.value}")
    before = item.status.value
    item.status = status
    if status == FreightInvoiceStatus.issued:
        item.issued_at = datetime.now(timezone.utc)
    if status == FreightInvoiceStatus.paid:
        item.paid_at = datetime.now(timezone.utc)
        item.amount_paid = item.total
        item.balance_due = Decimal("0")
    db.add(FreightEvent(
        tenant_id=user.tenant_id, entity_type="invoice", entity_id=item.id,
        event_type=f"invoice.{status.value}", actor_user_id=user.id,
        payload={"from": before, "to": status.value}, external_visible=True
    ))
    db.commit()
    return invoice_view(item)


@app.post("/v1/freight/documents", status_code=201)
async def upload_freight_document(
    entity_type: str,
    entity_id: str,
    document_type: str,
    external_visible: bool = True,
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    allowed = {
        "application/pdf", "text/csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel", "image/png", "image/jpeg"
    }
    safe_name = Path(file.filename or "document").name.replace("\x00", "")
    if file.content_type not in allowed:
        raise HTTPException(415, "Unsupported freight document type")
    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(413, "Document exceeds 25 MB")
    storage_key = f"{user.tenant_id}/freight/{entity_type}/{entity_id}/{uuid.uuid4()}-{safe_name}"
    local_root = Path(os.getenv("LOCAL_STORAGE_ROOT", "../../work/uploads")).resolve()
    target = (local_root / storage_key).resolve()
    if local_root not in target.parents:
        raise HTTPException(400, "Invalid document path")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    document = FreightDocument(
        tenant_id=user.tenant_id, entity_type=entity_type, entity_id=entity_id,
        document_type=document_type, filename=safe_name, storage_key=storage_key,
        content_type=file.content_type or "application/octet-stream", size_bytes=len(content),
        metadata_json={}, uploaded_by_id=user.id,
        external_visible=external_visible and not is_external_freight_user(user)
    )
    db.add(document)
    db.commit()
    return {"id": document.id, "filename": document.filename, "version": document.version}
