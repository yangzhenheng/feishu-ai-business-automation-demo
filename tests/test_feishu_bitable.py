import os

from fastapi.testclient import TestClient


def build_client(tmp_path, monkeypatch):
    monkeypatch.setenv("FEISHU_ENABLE_REAL_API", "false")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "bitable_test.db"))

    import app.db as db

    db.DB_PATH = os.environ["DATABASE_PATH"]
    db.init_db()

    from app.main import app

    return TestClient(app)


def test_feishu_bitable_status_and_sync_endpoints(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    status = client.get("/api/feishu/bitable/status")
    assert status.status_code == 200
    assert status.json()["current_mode"] == "mock"

    endpoints = [
        "/api/feishu/bitable/sync/orders",
        "/api/feishu/bitable/sync/inventory",
        "/api/feishu/bitable/sync/exceptions",
        "/api/feishu/bitable/sync/leads",
        "/api/feishu/bitable/sync/report",
        "/api/feishu/bitable/sync/all",
    ]
    for endpoint in endpoints:
        response = client.post(endpoint)
        assert response.status_code == 200
        payload = response.json()
        assert payload["mode"] == "mock"
        assert payload["ok"] is True
        assert payload["synced_records"] >= 0
        assert payload["next_action"]
        if endpoint.endswith("/all"):
            assert payload["total_synced_records"] >= payload["synced_records"]
            assert payload["synced_tables"] == ["orders", "inventory", "exceptions", "leads", "reports"]


def test_full_flow_contains_feishu_bitable_step(tmp_path, monkeypatch):
    client = build_client(tmp_path, monkeypatch)

    response = client.post("/api/demo/run-full-flow")
    assert response.status_code == 200
    payload = response.json()

    step_names = [step["name"] for step in payload["steps"]]
    assert "飞书多维表格同步" in step_names
    assert payload["feishu_bitable_sync"]["mode"] == "mock"
