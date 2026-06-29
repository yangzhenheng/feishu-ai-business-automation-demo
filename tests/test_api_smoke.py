import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "smoke.db"))
    monkeypatch.setenv("FEISHU_ENABLE_REAL_API", "false")
    monkeypatch.delenv("FEISHU_WEBHOOK_URL", raising=False)

    import app.db as db

    db.DB_PATH = os.environ["DATABASE_PATH"]

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


def test_core_get_endpoints_return_200(client):
    endpoints = [
        "/",
        "/health",
        "/docs",
        "/api/dashboard",
        "/api/sql/examples",
        "/api/workflow/logs",
        "/api/ecommerce/flow",
        "/api/mock/shop/orders",
        "/api/ai/roadmap",
        "/api/deployment/checklist",
        "/api/model-routing",
        "/api/feishu/bitable/status",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200, endpoint


def test_core_post_endpoints_return_200(client):
    post_cases = [
        ("/api/demo/run-full-flow", None),
        ("/api/ai/exception-classify", {"text": "黑色连衣裙库存不足，客户催单"}),
        ("/api/model-routing/select", {"task_type": "daily_report"}),
        ("/api/mock/shop/orders/sync", None),
        ("/api/mock/wms/inventory/check", None),
        ("/api/mock/logistics/track", None),
        ("/api/mock/finance/reconcile", None),
        ("/api/mock/crm/leads", None),
        ("/api/feishu/bitable/sync/orders", None),
        ("/api/feishu/bitable/sync/inventory", None),
        ("/api/feishu/bitable/sync/exceptions", None),
        ("/api/feishu/bitable/sync/leads", None),
        ("/api/feishu/bitable/sync/report", None),
        ("/api/feishu/bitable/sync/all", None),
    ]

    for endpoint, body in post_cases:
        response = client.post(endpoint, json=body) if body is not None else client.post(endpoint)
        assert response.status_code == 200, endpoint


def test_sql_examples_use_sqlite_rows(client):
    payload = client.get("/api/sql/examples").json()
    examples = payload["examples"]

    assert len(examples) == 5
    for example in examples:
        assert {"title", "description", "sql", "rows"} <= set(example)
        assert isinstance(example["rows"], list)


def test_full_flow_persists_workflow_log_and_bitable_sync(client):
    response = client.post("/api/demo/run-full-flow")
    assert response.status_code == 200
    payload = response.json()

    assert len(payload["steps"]) == 9
    for step in payload["steps"]:
        assert {"step", "name", "status", "detail", "business_value"} <= set(step)

    assert payload["feishu_webhook_status"]["status"] == "skipped"
    assert payload["feishu_bitable_sync"]["mode"] == "mock"
    assert payload["feishu_bitable_sync"]["total_synced_records"] >= 0
    assert payload["log_id"]

    logs = client.get("/api/workflow/logs").json()
    assert logs[0]["summary"]
    assert logs[0]["pushed_to_feishu"] == "skipped"
