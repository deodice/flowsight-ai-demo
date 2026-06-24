import os
os.environ["DATABASE_URL"] = "sqlite:///./test_flowsight.db"
os.environ["JWT_SECRET"] = "test-secret-that-is-longer-than-32-characters"
import pytest
from fastapi.testclient import TestClient
from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Role, User
from app.security import hash_password
from app.seed import seed_freight_data, seed_procurement_data, seed_tenant


@pytest.fixture(autouse=True)
def database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_tenant(db, "Industrial Distributor Demo", "industrial-distributor-demo", "industrial_distributor")
        freight_tenant = seed_tenant(db, "Keystone Freight Partners Demo", "keystone-freight-demo", "hybrid_freight")
        seed_freight_data(db, freight_tenant)
        seed_procurement_data(db, freight_tenant)
        db.add(User(
            tenant_id=freight_tenant.id, email="client@apex.demo", full_name="Alex Rivera",
            password_hash=hash_password("FlowSightDemo!"), role=Role.readonly_client, verified=True
        ))
        db.commit()
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def token(client):
    response = client.post("/v1/auth/login", json={
        "email": "maya@demo.flowsight.ai", "password": "FlowSightDemo!",
        "tenant_slug": "industrial-distributor-demo"
    })
    return response.json()["access_token"]


@pytest.fixture
def freight_token(client):
    response = client.post("/v1/auth/login", json={
        "email": "maya@demo.flowsight.ai", "password": "FlowSightDemo!",
        "tenant_slug": "keystone-freight-demo"
    })
    return response.json()["access_token"]


@pytest.fixture
def client_token(client):
    response = client.post("/v1/auth/login", json={
        "email": "client@apex.demo", "password": "FlowSightDemo!",
        "tenant_slug": "keystone-freight-demo"
    })
    return response.json()["access_token"]
