from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.db import get_connection, init_db
from app.services.business import (
    build_rule_based_report,
    classify_exception_text,
    command_response,
    customer_service_answer,
    get_dashboard,
)
from app.services.ai_roadmap import get_ai_roadmap
from app.services.ecommerce import get_deployment_checklist, get_ecommerce_flow
from app.services.erp_wms_crm import (
    check_inventory,
    collect_crm_leads,
    get_shop_orders,
    reconcile_finance,
    sync_shop_orders,
    track_logistics,
)
from app.services.llm import generate_llm_report
from app.services.notifier import notify_all
from app.services.model_router import get_all_routes, select_model
from app.services.feishu_design import get_feishu_design
from app.services.sql_examples import get_sql_examples

app = FastAPI(
    title="Feishu AI Business Automation Demo",
    description="AI + 飞书低代码 + 企业微信/飞书机器人 + AI客服 + 供应链业务自动化 Demo",
    version="1.0.0",
)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


class BotCommandRequest(BaseModel):
    command: str
    push_to_bot: bool = False


class CustomerServiceRequest(BaseModel):
    message: str
    name: str = "匿名客户"
    contact: Optional[str] = None
    save_lead: bool = True


class NotifyRequest(BaseModel):
    text: str


class ExceptionClassifyRequest(BaseModel):
    text: str


class ModelRouteRequest(BaseModel):
    task_type: str


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    html = (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")
    return html


@app.get("/health")
def health():
    return {"ok": True, "time": dt.datetime.now().isoformat()}


@app.get("/api/dashboard")
def api_dashboard():
    conn = get_connection()
    try:
        return get_dashboard(conn)
    finally:
        conn.close()


@app.get("/api/report/daily")
def api_daily_report(use_llm: bool = False):
    conn = get_connection()
    try:
        rule_report = build_rule_based_report(conn)
        report = generate_llm_report(rule_report) if use_llm else rule_report
        return {"report": report, "use_llm": use_llm}
    finally:
        conn.close()


@app.post("/api/bot/command")
def api_bot_command(req: BotCommandRequest):
    conn = get_connection()
    try:
        result = command_response(conn, req.command)
    finally:
        conn.close()

    notify_result = None
    if req.push_to_bot:
        notify_result = notify_all(result[:3500])
    return {"command": req.command, "result": result, "notify": notify_result}


@app.post("/api/customer-service")
def api_customer_service(req: CustomerServiceRequest):
    answer = customer_service_answer(req.message)

    if req.save_lead:
        conn = get_connection()
        try:
            conn.execute(
                """
                INSERT INTO leads(name, contact, demand, intent_level, source, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    req.name,
                    req.contact,
                    answer["demand"],
                    answer["intent_level"],
                    "AI客服Demo",
                    "待跟进",
                    dt.date.today().isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()
    return answer


@app.get("/api/feishu/design")
def api_feishu_design():
    return get_feishu_design()


@app.get("/api/model-routing")
def api_model_routing():
    return get_all_routes()


@app.post("/api/model-routing/select")
def api_model_routing_select(req: ModelRouteRequest):
    return select_model(req.task_type)


@app.post("/api/ai/exception-classify")
def api_exception_classify(req: ExceptionClassifyRequest):
    route = select_model("exception_classification")
    result = classify_exception_text(req.text)
    result["model_route"] = route
    return result


@app.post("/api/notify/test")
def api_notify_test(req: NotifyRequest):
    return notify_all(req.text)


@app.get("/api/ecommerce/flow")
def api_ecommerce_flow():
    return get_ecommerce_flow()


@app.get("/api/mock/shop/orders")
def api_mock_shop_orders():
    return {"orders": get_shop_orders()}


@app.post("/api/mock/shop/orders/sync")
def api_mock_shop_orders_sync():
    return sync_shop_orders()


@app.post("/api/mock/wms/inventory/check")
def api_mock_wms_inventory_check():
    return check_inventory()


@app.post("/api/mock/logistics/track")
def api_mock_logistics_track():
    return track_logistics()


@app.post("/api/mock/finance/reconcile")
def api_mock_finance_reconcile():
    return reconcile_finance()


@app.post("/api/mock/crm/leads")
def api_mock_crm_leads():
    return collect_crm_leads()


@app.get("/api/sql/examples")
def api_sql_examples():
    return get_sql_examples()


@app.get("/api/ai/roadmap")
def api_ai_roadmap():
    return get_ai_roadmap()


@app.get("/api/deployment/checklist")
def api_deployment_checklist():
    return get_deployment_checklist()
