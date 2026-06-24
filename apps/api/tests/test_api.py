def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_login_and_tenant_scoped_dashboard(client, token):
    response = client.get("/v1/dashboard", headers=auth(token))
    assert response.status_code == 200
    body = response.json()
    assert body["kpis"]["revenue_at_risk"] > 0
    assert len(body["priority_exceptions"]) >= 3


def test_exception_to_task_workflow(client, token):
    exceptions = client.get("/v1/exceptions", headers=auth(token)).json()
    item = exceptions[0]
    response = client.post("/v1/tasks", headers=auth(token), json={
        "exception_id": item["id"], "title": item["recommended_action"], "priority": "critical"
    })
    assert response.status_code == 201
    tasks = client.get("/v1/tasks", headers=auth(token)).json()
    assert len(tasks) == 1


def test_mapping_validation(client, token):
    response = client.post("/v1/imports/validate-mapping", headers=auth(token), json={
        "entity_type": "inventory_snapshot",
        "mapping": {"SKU_NUMBER": "sku", "WAREHOUSE": "site", "SNAPSHOT_DT": "snapshot_date", "QTY": "quantity_on_hand"}
    })
    assert response.json()["valid"] is True


def test_forecast_api(client, token):
    response = client.post("/v1/forecasts/run", headers=auth(token), json={
        "values": [10,12,11,14,15,13,17,18,19,21,20,24], "horizon": 4
    })
    assert response.status_code == 200
    assert len(response.json()["forecast"]) == 4


def test_new_tenant_onboarding_path(client):
    created = client.post("/v1/auth/register", json={
        "name": "Pilot Manufacturing", "slug": "pilot-manufacturing",
        "business_type": "light_manufacturer", "admin_email": "ops@pilot.example",
        "admin_name": "Alex Rivera", "password": "SecurePilot123!"
    })
    assert created.status_code == 201
    login = client.post("/v1/auth/login", json={
        "email": "ops@pilot.example", "password": "SecurePilot123!",
        "tenant_slug": "pilot-manufacturing"
    })
    assert login.status_code == 200


def test_tenant_isolation(client, token):
    from app.database import SessionLocal
    from app.seed import seed_tenant
    with SessionLocal() as db:
        seed_tenant(db, "Light Manufacturer Demo", "light-manufacturer-demo", "light_manufacturer")
    second_login = client.post("/v1/auth/login", json={
        "email": "maya@demo.flowsight.ai", "password": "FlowSightDemo!",
        "tenant_slug": "light-manufacturer-demo"
    }).json()
    first_ids = {item["id"] for item in client.get("/v1/exceptions", headers=auth(token)).json()}
    second_ids = {
        item["id"] for item in client.get(
            "/v1/exceptions", headers=auth(second_login["access_token"])
        ).json()
    }
    assert first_ids
    assert second_ids
    assert first_ids.isdisjoint(second_ids)
