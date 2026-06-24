from sqlalchemy import func, select
from app.database import SessionLocal
from app.models import BillingAccount, ExceptionEvent, FeatureFlag, Product, Site, Tenant


def test_demo_seed_contains_a_sellable_operating_story():
    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.slug == "industrial-distributor-demo"))
        assert tenant is not None
        assert tenant.is_demo is True
        assert db.scalar(select(func.count()).select_from(Site).where(Site.tenant_id == tenant.id)) == 3
        assert db.scalar(select(func.count()).select_from(Product).where(Product.tenant_id == tenant.id)) >= 3
        assert db.scalar(select(func.count()).select_from(ExceptionEvent).where(ExceptionEvent.tenant_id == tenant.id)) >= 5
        assert db.scalar(select(func.count()).select_from(FeatureFlag).where(FeatureFlag.tenant_id == tenant.id)) >= 4
        assert db.scalar(select(func.count()).select_from(BillingAccount).where(BillingAccount.tenant_id == tenant.id)) == 1
