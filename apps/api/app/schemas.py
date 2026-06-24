from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    tenant_slug: str = "industrial-distributor-demo"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class TenantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    slug: str = Field(pattern=r"^[a-z0-9-]+$")
    business_type: str
    admin_email: EmailStr
    admin_name: str
    password: str = Field(min_length=10)


class ExceptionOut(ORMModel):
    id: str
    code: str
    exception_type: str
    title: str
    detail: str
    severity: str
    severity_score: float
    confidence_score: float
    estimated_impact: float
    contributing_factors: list
    related_records: list
    recommended_action: str
    status: str
    owner_id: str | None
    due_at: datetime | None


class TaskCreate(BaseModel):
    exception_id: str | None = None
    title: str
    description: str | None = None
    owner_id: str | None = None
    due_at: datetime | None = None
    priority: str = "medium"


class FeedbackCreate(BaseModel):
    kind: str
    module: str
    severity: str | None = None
    message: str = Field(min_length=5)
    tags: list[str] = []


class ForecastRequest(BaseModel):
    product_id: str | None = None
    values: list[float] = Field(min_length=8)
    horizon: int = Field(default=8, ge=1, le=52)


class ImportMappingRequest(BaseModel):
    entity_type: str
    mapping: dict[str, str]
    partial_import: bool = True


class FreightDimension(BaseModel):
    length: float = Field(gt=0)
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    pieces: int = Field(default=1, ge=1)


class FreightQuoteRequest(BaseModel):
    mode: str
    origin: str
    destination: str
    distance_miles: float = Field(gt=0)
    weight_lb: float = Field(gt=0)
    pallet_count: int = Field(default=0, ge=0)
    equipment: str | None = None
    service_level: str | None = None
    freight_class: str | None = None
    accessorials: list[str] = Field(default_factory=list)
    hazmat: bool = False
    target_margin_pct: float = Field(default=20, gt=0, lt=95)
    fuel_surcharge_pct: float = Field(default=18.5, ge=0, le=100)
    pieces: int = Field(default=1, ge=1)
    dimensions_in: list[FreightDimension] = Field(default_factory=list)
    customer_id: str | None = None
    carrier_id: str | None = None
    lane_history: dict[str, float] = Field(default_factory=dict)
    workspace: str = "internal"


class FreightQuoteCreate(FreightQuoteRequest):
    tender_id: str | None = None


class TenderCreate(BaseModel):
    mode: str
    customer_id: str | None = None
    carrier_id: str | None = None
    lane_id: str | None = None
    shipment_id: str | None = None
    quoted_amount: float | None = None
    internal_cost: float | None = None
    target_margin_pct: float | None = None
    expires_at: datetime | None = None
    client_notes: str | None = None
    internal_notes: str | None = None


class InvoiceCreate(BaseModel):
    shipment_id: str | None = None
    tender_id: str | None = None
    quote_id: str | None = None
    customer_id: str | None = None
    due_at: datetime | None = None
    quoted_total: float | None = None
    line_items: list[dict]


class CarrierCreate(BaseModel):
    code: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=2, max_length=255)
    tier: str = "standard"
    classification: str = "carrier"
    covered_modes: list[str] = Field(default_factory=list)
    headquarters: dict = Field(default_factory=dict)
    regions_served: list[str] = Field(default_factory=list)
    government_business: bool = False
    sddc_registered: bool = False
    gfm_approved: bool = False
    dod_relevant: bool = False
    website: str | None = None
    primary_contact_name: str | None = None
    primary_contact_email: EmailStr | None = None
    primary_contact_phone: str | None = None
    notes: str | None = None
    authority_status: str = "active"
    insurance_expires_on: date | None = None
    hazmat_capable: bool = False
    refrigerated_capable: bool = False
    relationship_status: str = "unknown"
    compliance_status: str = "incomplete"
    performance_score: float = Field(default=0, ge=0, le=100)


class OpportunityCreate(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    customer_program: str | None = None
    contract_number: str | None = None
    origin: dict
    destination: dict
    pickup_at: datetime
    delivery_at: datetime | None = None
    quote_deadline: datetime | None = None
    mode: str
    weight_lb: float = Field(gt=0)
    dimensions: list[dict] = Field(default_factory=list)
    commodity: str = Field(min_length=2, max_length=255)
    hazmat: bool = False
    refrigerated: bool = False
    government_relevance: bool = False
    sddc_relevance: bool = False
    gfm_relevance: bool = False
    notes: str | None = None
    required_compliance_tags: list[str] = Field(default_factory=list)
    required_documents: list[str] = Field(default_factory=list)
    priority: str = "normal"


class OpportunityShortlist(BaseModel):
    carrier_ids: list[str] = Field(min_length=1)


class OpportunityCarrierStatusUpdate(BaseModel):
    status: str


class RFQGenerateRequest(BaseModel):
    carrier_ids: list[str] = Field(default_factory=list)


class CarrierBidCreate(BaseModel):
    carrier_id: str
    amount: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    transit_days: float | None = Field(default=None, gt=0)
    accessorials: list[dict] = Field(default_factory=list)
    fuel_surcharge: float = Field(default=0, ge=0)
    expires_at: datetime | None = None
    carrier_contact: str | None = None
    notes: str | None = None
    status: str = "received"


class AwardCreate(BaseModel):
    carrier_id: str
    bid_id: str | None = None
    rationale: str = Field(min_length=5)
