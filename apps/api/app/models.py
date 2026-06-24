import enum
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import (
    JSON, Boolean, Date, DateTime, Enum, Float, ForeignKey, Index, Integer,
    Numeric, String, Text, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def uid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Role(str, enum.Enum):
    platform_admin = "platform_super_admin"
    tenant_admin = "tenant_admin"
    executive = "executive_viewer"
    operations = "operations_manager"
    analyst = "analyst"
    readonly = "read_only_viewer"
    sales_quote_desk = "sales_quote_desk"
    dispatch_execution = "dispatch_execution"
    billing_finance = "billing_finance"
    readonly_client = "read_only_client"
    readonly_partner = "read_only_external_partner"


class Plan(str, enum.Enum):
    pilot = "pilot"
    starter = "starter"
    growth = "growth"
    scale = "scale"


class ExceptionStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    dismissed = "dismissed"


class LoadMode(str, enum.Enum):
    small_parcel = "small_parcel"
    ltl = "ltl"
    tl = "tl"
    spot_bid = "spot_bid"
    air_freight = "air_freight"
    other = "other"


class OpportunityStatus(str, enum.Enum):
    draft = "draft"
    sourcing = "sourcing"
    rfq_open = "rfq_open"
    evaluating = "evaluating"
    awarded = "awarded"
    closed = "closed"
    canceled = "canceled"


class OpportunityCarrierStatus(str, enum.Enum):
    not_contacted = "not_contacted"
    shortlisted = "shortlisted"
    rfq_sent = "rfq_sent"
    responded = "responded"
    no_bid = "no_bid"
    quoted = "quoted"
    awarded = "awarded"
    rejected = "rejected"


class TenderStatus(str, enum.Enum):
    draft = "draft"
    issued = "issued"
    countered = "countered"
    accepted = "accepted"
    rejected = "rejected"
    expired = "expired"
    awarded = "awarded"
    in_transit = "in_transit"
    delivered = "delivered"
    invoiced = "invoiced"
    paid = "paid"
    disputed = "disputed"
    closed = "closed"


class FreightInvoiceStatus(str, enum.Enum):
    draft = "draft"
    issued = "issued"
    sent = "sent"
    partially_paid = "partially_paid"
    paid = "paid"
    past_due = "past_due"
    on_hold = "on_hold"
    disputed = "disputed"
    credited = "credited"
    voided = "voided"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    business_type: Mapped[str] = mapped_column(String(80), default="industrial_distributor")
    plan: Mapped[Plan] = mapped_column(Enum(Plan), default=Plan.pilot)
    timezone: Mapped[str] = mapped_column(String(64), default="America/New_York")
    brand_color: Mapped[str] = mapped_column(String(16), default="#167f74")
    logo_url: Mapped[str | None] = mapped_column(String(500))
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime)


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(180))
    external_id: Mapped[str | None] = mapped_column(String(120))


class Site(Base, TimestampMixin):
    __tablename__ = "sites"
    __table_args__ = (UniqueConstraint("tenant_id", "code"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"))
    code: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(180))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(40))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class User(Base, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("tenant_id", "email"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    full_name: Mapped[str] = mapped_column(String(180))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.analyst)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    mfa_secret: Mapped[str | None] = mapped_column(String(255))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)


class Product(Base, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("tenant_id", "sku"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    sku: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(120))
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    lead_time_days: Mapped[int | None] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    attributes: Mapped[dict] = mapped_column(JSON, default=dict)


class Supplier(Base, TimestampMixin):
    __tablename__ = "suppliers"
    __table_args__ = (UniqueConstraint("tenant_id", "code"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    code: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    planned_lead_time_days: Mapped[int | None] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"
    __table_args__ = (UniqueConstraint("tenant_id", "code"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    code: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(255))
    tier: Mapped[str | None] = mapped_column(String(50))


class Carrier(Base, TimestampMixin):
    __tablename__ = "carriers"
    __table_args__ = (UniqueConstraint("tenant_id", "code"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    code: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(255))
    tier: Mapped[str] = mapped_column(String(40), default="standard")
    classification: Mapped[str] = mapped_column(String(40), default="carrier")
    covered_modes: Mapped[list] = mapped_column(JSON, default=list)
    headquarters: Mapped[dict] = mapped_column(JSON, default=dict)
    regions_served: Mapped[list] = mapped_column(JSON, default=list)
    government_business: Mapped[bool] = mapped_column(Boolean, default=False)
    sddc_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    gfm_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    dod_relevant: Mapped[bool] = mapped_column(Boolean, default=False)
    website: Mapped[str | None] = mapped_column(String(500))
    primary_contact_name: Mapped[str | None] = mapped_column(String(180))
    primary_contact_email: Mapped[str | None] = mapped_column(String(255))
    primary_contact_phone: Mapped[str | None] = mapped_column(String(60))
    notes: Mapped[str | None] = mapped_column(Text)
    authority_status: Mapped[str] = mapped_column(String(40), default="active")
    insurance_expires_on: Mapped[date | None] = mapped_column(Date)
    hazmat_capable: Mapped[bool] = mapped_column(Boolean, default=False)
    refrigerated_capable: Mapped[bool] = mapped_column(Boolean, default=False)
    relationship_status: Mapped[str] = mapped_column(String(40), default="unknown")
    compliance_status: Mapped[str] = mapped_column(String(40), default="incomplete")
    last_contacted_at: Mapped[datetime | None] = mapped_column(DateTime)
    performance_score: Mapped[float] = mapped_column(Float, default=0)
    prior_awards: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Contact(Base, TimestampMixin):
    __tablename__ = "contacts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"), index=True)
    carrier_id: Mapped[str | None] = mapped_column(ForeignKey("carriers.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(180))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(60))
    role_title: Mapped[str | None] = mapped_column(String(120))
    external_visible: Mapped[bool] = mapped_column(Boolean, default=True)


class Shipper(Base, TimestampMixin):
    __tablename__ = "shippers"
    __table_args__ = (UniqueConstraint("tenant_id", "code"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id"))
    code: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(255))
    address: Mapped[dict] = mapped_column(JSON, default=dict)


class Consignee(Base, TimestampMixin):
    __tablename__ = "consignees"
    __table_args__ = (UniqueConstraint("tenant_id", "code"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    code: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(255))
    address: Mapped[dict] = mapped_column(JSON, default=dict)
    appointment_required: Mapped[bool] = mapped_column(Boolean, default=False)


class Lane(Base, TimestampMixin):
    __tablename__ = "lanes"
    __table_args__ = (UniqueConstraint("tenant_id", "code"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    code: Mapped[str] = mapped_column(String(100))
    origin: Mapped[dict] = mapped_column(JSON)
    destination: Mapped[dict] = mapped_column(JSON)
    distance_miles: Mapped[float | None] = mapped_column(Float)
    default_mode: Mapped[LoadMode | None] = mapped_column(Enum(LoadMode))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class CarrierComplianceDocument(Base, TimestampMixin):
    __tablename__ = "carrier_compliance_documents"
    __table_args__ = (UniqueConstraint("carrier_id", "document_type"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    carrier_id: Mapped[str] = mapped_column(ForeignKey("carriers.id"), index=True)
    document_type: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(40), default="missing")
    expires_on: Mapped[date | None] = mapped_column(Date)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class FreightOpportunity(Base, TimestampMixin):
    __tablename__ = "freight_opportunities"
    __table_args__ = (UniqueConstraint("tenant_id", "opportunity_number"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    opportunity_number: Mapped[str] = mapped_column(String(100), index=True)
    name: Mapped[str] = mapped_column(String(255))
    customer_program: Mapped[str | None] = mapped_column(String(255))
    contract_number: Mapped[str | None] = mapped_column(String(120))
    origin: Mapped[dict] = mapped_column(JSON)
    destination: Mapped[dict] = mapped_column(JSON)
    pickup_at: Mapped[datetime] = mapped_column(DateTime)
    delivery_at: Mapped[datetime | None] = mapped_column(DateTime)
    quote_deadline: Mapped[datetime | None] = mapped_column(DateTime)
    mode: Mapped[LoadMode] = mapped_column(Enum(LoadMode), index=True)
    weight_lb: Mapped[float] = mapped_column(Float)
    dimensions: Mapped[list] = mapped_column(JSON, default=list)
    commodity: Mapped[str] = mapped_column(String(255))
    hazmat: Mapped[bool] = mapped_column(Boolean, default=False)
    refrigerated: Mapped[bool] = mapped_column(Boolean, default=False)
    government_relevance: Mapped[bool] = mapped_column(Boolean, default=False)
    sddc_relevance: Mapped[bool] = mapped_column(Boolean, default=False)
    gfm_relevance: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)
    required_compliance_tags: Mapped[list] = mapped_column(JSON, default=list)
    required_documents: Mapped[list] = mapped_column(JSON, default=list)
    priority: Mapped[str] = mapped_column(String(30), default="normal")
    status: Mapped[OpportunityStatus] = mapped_column(Enum(OpportunityStatus), default=OpportunityStatus.draft, index=True)
    owner_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    awarded_carrier_id: Mapped[str | None] = mapped_column(ForeignKey("carriers.id"))
    decision_rationale: Mapped[str | None] = mapped_column(Text)
    awarded_at: Mapped[datetime | None] = mapped_column(DateTime)


class OpportunityCarrier(Base, TimestampMixin):
    __tablename__ = "opportunity_carriers"
    __table_args__ = (UniqueConstraint("opportunity_id", "carrier_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("freight_opportunities.id"), index=True)
    carrier_id: Mapped[str] = mapped_column(ForeignKey("carriers.id"), index=True)
    status: Mapped[OpportunityCarrierStatus] = mapped_column(
        Enum(OpportunityCarrierStatus), default=OpportunityCarrierStatus.not_contacted, index=True
    )
    shortlisted: Mapped[bool] = mapped_column(Boolean, default=False)
    match_score: Mapped[float] = mapped_column(Float, default=0)
    score_breakdown: Mapped[list] = mapped_column(JSON, default=list)
    manual_adjustment: Mapped[float] = mapped_column(Float, default=0)
    rfq_subject: Mapped[str | None] = mapped_column(String(255))
    rfq_body: Mapped[str | None] = mapped_column(Text)
    rfq_generated_at: Mapped[datetime | None] = mapped_column(DateTime)
    rfq_sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime)


class CarrierBid(Base, TimestampMixin):
    __tablename__ = "carrier_bids"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("freight_opportunities.id"), index=True)
    opportunity_carrier_id: Mapped[str] = mapped_column(ForeignKey("opportunity_carriers.id"), index=True)
    carrier_id: Mapped[str] = mapped_column(ForeignKey("carriers.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    transit_days: Mapped[float | None] = mapped_column(Float)
    accessorials: Mapped[list] = mapped_column(JSON, default=list)
    fuel_surcharge: Mapped[Decimal] = mapped_column(Numeric(16, 2), default=0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    carrier_contact: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="received")
    received_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class FreightAward(Base, TimestampMixin):
    __tablename__ = "freight_awards"
    __table_args__ = (UniqueConstraint("opportunity_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    opportunity_id: Mapped[str] = mapped_column(ForeignKey("freight_opportunities.id"), index=True)
    carrier_id: Mapped[str] = mapped_column(ForeignKey("carriers.id"), index=True)
    bid_id: Mapped[str | None] = mapped_column(ForeignKey("carrier_bids.id"))
    awarded_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    rationale: Mapped[str] = mapped_column(Text)
    score_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    awarded_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class FreightShipment(Base, TimestampMixin):
    __tablename__ = "freight_shipments"
    __table_args__ = (UniqueConstraint("tenant_id", "shipment_number"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    shipment_number: Mapped[str] = mapped_column(String(100), index=True)
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id"))
    carrier_id: Mapped[str | None] = mapped_column(ForeignKey("carriers.id"))
    shipper_id: Mapped[str | None] = mapped_column(ForeignKey("shippers.id"))
    consignee_id: Mapped[str | None] = mapped_column(ForeignKey("consignees.id"))
    lane_id: Mapped[str | None] = mapped_column(ForeignKey("lanes.id"))
    mode: Mapped[LoadMode] = mapped_column(Enum(LoadMode), index=True)
    status: Mapped[str] = mapped_column(String(40), default="planned")
    equipment: Mapped[str | None] = mapped_column(String(120))
    service_level: Mapped[str | None] = mapped_column(String(120))
    weight_lb: Mapped[float | None] = mapped_column(Float)
    pallet_count: Mapped[int | None] = mapped_column(Integer)
    freight_class: Mapped[str | None] = mapped_column(String(30))
    hazmat: Mapped[bool] = mapped_column(Boolean, default=False)
    pickup_at: Mapped[datetime | None] = mapped_column(DateTime)
    delivery_at: Mapped[datetime | None] = mapped_column(DateTime)
    actual_pickup_at: Mapped[datetime | None] = mapped_column(DateTime)
    actual_delivery_at: Mapped[datetime | None] = mapped_column(DateTime)
    awb_number: Mapped[str | None] = mapped_column(String(80))
    mawb_number: Mapped[str | None] = mapped_column(String(80))
    hawb_number: Mapped[str | None] = mapped_column(String(80))
    origin_airport: Mapped[str | None] = mapped_column(String(8))
    destination_airport: Mapped[str | None] = mapped_column(String(8))
    actual_weight_kg: Mapped[float | None] = mapped_column(Float)
    dimensional_weight_kg: Mapped[float | None] = mapped_column(Float)
    chargeable_weight_kg: Mapped[float | None] = mapped_column(Float)
    uplift_at: Mapped[datetime | None] = mapped_column(DateTime)
    departed_at: Mapped[datetime | None] = mapped_column(DateTime)
    arrived_at: Mapped[datetime | None] = mapped_column(DateTime)
    internal_cost: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    client_charge: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    internal_notes: Mapped[str | None] = mapped_column(Text)


class FreightTender(Base, TimestampMixin):
    __tablename__ = "freight_tenders"
    __table_args__ = (UniqueConstraint("tenant_id", "tender_number"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    tender_number: Mapped[str] = mapped_column(String(100), index=True)
    shipment_id: Mapped[str | None] = mapped_column(ForeignKey("freight_shipments.id"), index=True)
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id"))
    carrier_id: Mapped[str | None] = mapped_column(ForeignKey("carriers.id"))
    lane_id: Mapped[str | None] = mapped_column(ForeignKey("lanes.id"))
    mode: Mapped[LoadMode] = mapped_column(Enum(LoadMode), index=True)
    status: Mapped[TenderStatus] = mapped_column(Enum(TenderStatus), default=TenderStatus.draft, index=True)
    issued_at: Mapped[datetime | None] = mapped_column(DateTime)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    awarded_at: Mapped[datetime | None] = mapped_column(DateTime)
    quoted_amount: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    internal_cost: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    target_margin_pct: Mapped[float | None] = mapped_column(Float)
    owner_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    client_notes: Mapped[str | None] = mapped_column(Text)
    internal_notes: Mapped[str | None] = mapped_column(Text)


class TenderRevision(Base, TimestampMixin):
    __tablename__ = "tender_revisions"
    __table_args__ = (UniqueConstraint("tender_id", "revision_number"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    tender_id: Mapped[str] = mapped_column(ForeignKey("freight_tenders.id"), index=True)
    revision_number: Mapped[int] = mapped_column(Integer)
    changed_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    snapshot: Mapped[dict] = mapped_column(JSON)
    change_reason: Mapped[str | None] = mapped_column(Text)


class FreightQuote(Base, TimestampMixin):
    __tablename__ = "freight_quotes"
    __table_args__ = (UniqueConstraint("tenant_id", "quote_number"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    quote_number: Mapped[str] = mapped_column(String(100), index=True)
    tender_id: Mapped[str | None] = mapped_column(ForeignKey("freight_tenders.id"))
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id"))
    carrier_id: Mapped[str | None] = mapped_column(ForeignKey("carriers.id"))
    lane_id: Mapped[str | None] = mapped_column(ForeignKey("lanes.id"))
    mode: Mapped[LoadMode] = mapped_column(Enum(LoadMode), index=True)
    status: Mapped[str] = mapped_column(String(40), default="draft")
    valid_until: Mapped[datetime | None] = mapped_column(DateTime)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    internal_cost: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    client_total: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    margin_amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    margin_pct: Mapped[float] = mapped_column(Float)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    calculation_input: Mapped[dict] = mapped_column(JSON)
    calculation_trace: Mapped[list] = mapped_column(JSON)
    explanation: Mapped[str | None] = mapped_column(Text)


class QuoteLineItem(Base, TimestampMixin):
    __tablename__ = "quote_line_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    quote_id: Mapped[str] = mapped_column(ForeignKey("freight_quotes.id"), index=True)
    code: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[float] = mapped_column(Float, default=1)
    unit_rate: Mapped[Decimal] = mapped_column(Numeric(16, 4))
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    cost_amount: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    external_visible: Mapped[bool] = mapped_column(Boolean, default=True)


class RateCard(Base, TimestampMixin):
    __tablename__ = "rate_cards"
    __table_args__ = (UniqueConstraint("tenant_id", "name", "version"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(180))
    scope_type: Mapped[str] = mapped_column(String(50))
    scope_id: Mapped[str | None] = mapped_column(String(36))
    mode: Mapped[LoadMode] = mapped_column(Enum(LoadMode), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[dict] = mapped_column(JSON)


class RateRule(Base, TimestampMixin):
    __tablename__ = "rate_rules"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    rate_card_id: Mapped[str | None] = mapped_column(ForeignKey("rate_cards.id"), index=True)
    name: Mapped[str] = mapped_column(String(180))
    rule_type: Mapped[str] = mapped_column(String(80))
    priority: Mapped[int] = mapped_column(Integer, default=100)
    conditions: Mapped[dict] = mapped_column(JSON, default=dict)
    calculation: Mapped[dict] = mapped_column(JSON)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class AccessorialRule(Base, TimestampMixin):
    __tablename__ = "accessorial_rules"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    rate_card_id: Mapped[str | None] = mapped_column(ForeignKey("rate_cards.id"), index=True)
    code: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(255))
    charge_type: Mapped[str] = mapped_column(String(40))
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 4))
    conditions: Mapped[dict] = mapped_column(JSON, default=dict)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class FreightInvoice(Base, TimestampMixin):
    __tablename__ = "freight_invoices"
    __table_args__ = (UniqueConstraint("tenant_id", "invoice_number"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    invoice_number: Mapped[str] = mapped_column(String(100), index=True)
    shipment_id: Mapped[str | None] = mapped_column(ForeignKey("freight_shipments.id"))
    tender_id: Mapped[str | None] = mapped_column(ForeignKey("freight_tenders.id"))
    quote_id: Mapped[str | None] = mapped_column(ForeignKey("freight_quotes.id"))
    customer_id: Mapped[str | None] = mapped_column(ForeignKey("customers.id"))
    status: Mapped[FreightInvoiceStatus] = mapped_column(Enum(FreightInvoiceStatus), default=FreightInvoiceStatus.draft, index=True)
    issued_at: Mapped[datetime | None] = mapped_column(DateTime)
    due_at: Mapped[datetime | None] = mapped_column(DateTime)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime)
    quoted_total: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(16, 2), default=0)
    tax_total: Mapped[Decimal] = mapped_column(Numeric(16, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(16, 2), default=0)
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(16, 2), default=0)
    balance_due: Mapped[Decimal] = mapped_column(Numeric(16, 2), default=0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    external_reference: Mapped[str | None] = mapped_column(String(160))


class InvoiceLineItem(Base, TimestampMixin):
    __tablename__ = "invoice_line_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    invoice_id: Mapped[str] = mapped_column(ForeignKey("freight_invoices.id"), index=True)
    code: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(String(255))
    quantity: Mapped[float] = mapped_column(Float, default=1)
    unit_rate: Mapped[Decimal] = mapped_column(Numeric(16, 4))
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))


class CreditAdjustment(Base, TimestampMixin):
    __tablename__ = "credit_adjustments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    invoice_id: Mapped[str] = mapped_column(ForeignKey("freight_invoices.id"), index=True)
    adjustment_number: Mapped[str] = mapped_column(String(100))
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    reason_code: Mapped[str] = mapped_column(String(80))
    note: Mapped[str | None] = mapped_column(Text)
    issued_at: Mapped[datetime | None] = mapped_column(DateTime)


class FreightDocument(Base, TimestampMixin):
    __tablename__ = "freight_documents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(60), index=True)
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    document_type: Mapped[str] = mapped_column(String(60))
    filename: Mapped[str] = mapped_column(String(255))
    storage_key: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str] = mapped_column(String(120))
    size_bytes: Mapped[int] = mapped_column(Integer)
    version: Mapped[int] = mapped_column(Integer, default=1)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    uploaded_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    external_visible: Mapped[bool] = mapped_column(Boolean, default=True)


class FreightEvent(Base):
    __tablename__ = "freight_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(60), index=True)
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    external_visible: Mapped[bool] = mapped_column(Boolean, default=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)


class Dispute(Base, TimestampMixin):
    __tablename__ = "disputes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    invoice_id: Mapped[str] = mapped_column(ForeignKey("freight_invoices.id"), index=True)
    opened_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(40), default="open")
    reason_code: Mapped[str] = mapped_column(String(80))
    disputed_amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    description: Mapped[str] = mapped_column(Text)
    resolution: Mapped[str | None] = mapped_column(Text)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)


class InventorySnapshot(Base, TimestampMixin):
    __tablename__ = "inventory_snapshots"
    __table_args__ = (Index("ix_inventory_tenant_product_date", "tenant_id", "product_id", "snapshot_date"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    site_id: Mapped[str] = mapped_column(ForeignKey("sites.id"))
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    snapshot_date: Mapped[date] = mapped_column(Date)
    quantity_on_hand: Mapped[float] = mapped_column(Float)
    quantity_allocated: Mapped[float] = mapped_column(Float, default=0)
    quantity_on_order: Mapped[float] = mapped_column(Float, default=0)
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))


class PurchaseOrder(Base, TimestampMixin):
    __tablename__ = "purchase_orders"
    __table_args__ = (UniqueConstraint("tenant_id", "po_number"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    site_id: Mapped[str] = mapped_column(ForeignKey("sites.id"))
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id"))
    po_number: Mapped[str] = mapped_column(String(100), index=True)
    order_date: Mapped[date] = mapped_column(Date)
    promised_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(40), default="open")
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    total_value: Mapped[Decimal] = mapped_column(Numeric(16, 2), default=0)
    lines: Mapped[list["PurchaseOrderLine"]] = relationship(cascade="all, delete-orphan")


class PurchaseOrderLine(Base, TimestampMixin):
    __tablename__ = "purchase_order_lines"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    purchase_order_id: Mapped[str] = mapped_column(ForeignKey("purchase_orders.id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    line_number: Mapped[int] = mapped_column(Integer)
    ordered_quantity: Mapped[float] = mapped_column(Float)
    received_quantity: Mapped[float] = mapped_column(Float, default=0)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(14, 4))


class SalesOrder(Base, TimestampMixin):
    __tablename__ = "sales_orders"
    __table_args__ = (UniqueConstraint("tenant_id", "order_number"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    site_id: Mapped[str] = mapped_column(ForeignKey("sites.id"))
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    order_number: Mapped[str] = mapped_column(String(100))
    order_date: Mapped[date] = mapped_column(Date)
    requested_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(40), default="open")


class OrderLine(Base, TimestampMixin):
    __tablename__ = "order_lines"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    sales_order_id: Mapped[str] = mapped_column(ForeignKey("sales_orders.id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    line_number: Mapped[int] = mapped_column(Integer)
    ordered_quantity: Mapped[float] = mapped_column(Float)
    shipped_quantity: Mapped[float] = mapped_column(Float, default=0)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 4))


class Shipment(Base, TimestampMixin):
    __tablename__ = "shipments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    carrier_id: Mapped[str | None] = mapped_column(ForeignKey("carriers.id"))
    shipment_number: Mapped[str] = mapped_column(String(100))
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime)
    promised_delivery_at: Mapped[datetime | None] = mapped_column(DateTime)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(40))


class ShipmentLine(Base, TimestampMixin):
    __tablename__ = "shipment_lines"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    shipment_id: Mapped[str] = mapped_column(ForeignKey("shipments.id"))
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[float] = mapped_column(Float)


class Receipt(Base, TimestampMixin):
    __tablename__ = "receipts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    site_id: Mapped[str] = mapped_column(ForeignKey("sites.id"))
    purchase_order_id: Mapped[str | None] = mapped_column(ForeignKey("purchase_orders.id"))
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"))
    receipt_date: Mapped[date] = mapped_column(Date)
    quantity: Mapped[float] = mapped_column(Float)


class ForecastRun(Base, TimestampMixin):
    __tablename__ = "forecast_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), index=True)
    site_id: Mapped[str | None] = mapped_column(ForeignKey("sites.id"))
    model_name: Mapped[str] = mapped_column(String(80))
    horizon: Mapped[int] = mapped_column(Integer)
    score_name: Mapped[str] = mapped_column(String(30), default="wape")
    score_value: Mapped[float] = mapped_column(Float)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    results: Mapped[dict] = mapped_column(JSON, default=dict)
    user_override: Mapped[dict | None] = mapped_column(JSON)


class AnomalyEvent(Base, TimestampMixin):
    __tablename__ = "anomaly_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    metric: Mapped[str] = mapped_column(String(100))
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    observed_value: Mapped[float] = mapped_column(Float)
    expected_value: Mapped[float] = mapped_column(Float)
    robust_z_score: Mapped[float] = mapped_column(Float)
    explanation: Mapped[str] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime)


class ExceptionEvent(Base, TimestampMixin):
    __tablename__ = "exception_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    code: Mapped[str] = mapped_column(String(40), index=True)
    exception_type: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(255))
    detail: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20))
    severity_score: Mapped[float] = mapped_column(Float)
    confidence_score: Mapped[float] = mapped_column(Float)
    estimated_impact: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    contributing_factors: Mapped[list] = mapped_column(JSON, default=list)
    related_records: Mapped[list] = mapped_column(JSON, default=list)
    recommended_action: Mapped[str] = mapped_column(Text)
    status: Mapped[ExceptionStatus] = mapped_column(Enum(ExceptionStatus), default=ExceptionStatus.open)
    owner_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    due_at: Mapped[datetime | None] = mapped_column(DateTime)
    usefulness: Mapped[int | None] = mapped_column(Integer)
    false_positive_reason: Mapped[str | None] = mapped_column(Text)


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    exception_id: Mapped[str | None] = mapped_column(ForeignKey("exception_events.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    due_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(30), default="open")
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    root_cause_tags: Mapped[list] = mapped_column(JSON, default=list)
    resolution_outcome: Mapped[str | None] = mapped_column(Text)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)


class Comment(Base, TimestampMixin):
    __tablename__ = "comments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
    attachment_keys: Mapped[list] = mapped_column(JSON, default=list)


class Scorecard(Base, TimestampMixin):
    __tablename__ = "scorecards"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[str] = mapped_column(String(36))
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    metrics: Mapped[dict] = mapped_column(JSON)


class ImportMapping(Base, TimestampMixin):
    __tablename__ = "import_mappings"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    entity_type: Mapped[str] = mapped_column(String(80))
    mapping: Mapped[dict] = mapped_column(JSON)
    transforms: Mapped[dict] = mapped_column(JSON, default=dict)


class ImportJob(Base, TimestampMixin):
    __tablename__ = "import_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    mapping_id: Mapped[str | None] = mapped_column(ForeignKey("import_mappings.id"))
    entity_type: Mapped[str] = mapped_column(String(80))
    filename: Mapped[str] = mapped_column(String(255))
    storage_key: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(30), default="uploaded")
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    accepted_count: Mapped[int] = mapped_column(Integer, default=0)
    rejected_count: Mapped[int] = mapped_column(Integer, default=0)
    detected_metadata: Mapped[dict] = mapped_column(JSON, default=dict)


class ValidationIssue(Base, TimestampMixin):
    __tablename__ = "validation_issues"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    import_job_id: Mapped[str] = mapped_column(ForeignKey("import_jobs.id"), index=True)
    row_number: Mapped[int] = mapped_column(Integer)
    field: Mapped[str | None] = mapped_column(String(100))
    code: Mapped[str] = mapped_column(String(80))
    message: Mapped[str] = mapped_column(Text)
    raw_row: Mapped[dict] = mapped_column(JSON)


class FeedbackItem(Base, TimestampMixin):
    __tablename__ = "feedback_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    kind: Mapped[str] = mapped_column(String(60))
    module: Mapped[str] = mapped_column(String(60))
    severity: Mapped[str | None] = mapped_column(String(30))
    message: Mapped[str] = mapped_column(Text)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(30), default="new")


class FeatureFlag(Base, TimestampMixin):
    __tablename__ = "feature_flags"
    __table_args__ = (UniqueConstraint("tenant_id", "key"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    key: Mapped[str] = mapped_column(String(100))
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict)


class BillingAccount(Base, TimestampMixin):
    __tablename__ = "billing_accounts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), unique=True)
    provider_customer_id: Mapped[str | None] = mapped_column(String(255))
    provider_subscription_id: Mapped[str | None] = mapped_column(String(255))
    plan: Mapped[Plan] = mapped_column(Enum(Plan))
    status: Mapped[str] = mapped_column(String(40), default="trialing")
    entitlements: Mapped[dict] = mapped_column(JSON, default=dict)


class ReportPreset(Base, TimestampMixin):
    __tablename__ = "report_presets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    role: Mapped[str | None] = mapped_column(String(60))
    format: Mapped[str] = mapped_column(String(20), default="pdf")
    config: Mapped[dict] = mapped_column(JSON)
    schedule: Mapped[dict | None] = mapped_column(JSON)


class AIGeneration(Base, TimestampMixin):
    __tablename__ = "ai_generations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    feature: Mapped[str] = mapped_column(String(80))
    prompt_hash: Mapped[str] = mapped_column(String(64))
    prompt_redacted: Mapped[str] = mapped_column(Text)
    output: Mapped[str] = mapped_column(Text)
    model: Mapped[str] = mapped_column(String(100))
    latency_ms: Mapped[int] = mapped_column(Integer)
    citations: Mapped[list] = mapped_column(JSON, default=list)
    feedback: Mapped[int | None] = mapped_column(Integer)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str | None] = mapped_column(ForeignKey("tenants.id"), index=True)
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(120), index=True)
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[str | None] = mapped_column(String(36))
    before: Mapped[dict | None] = mapped_column(JSON)
    after: Mapped[dict | None] = mapped_column(JSON)
    request_id: Mapped[str | None] = mapped_column(String(64))
    ip_address: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
