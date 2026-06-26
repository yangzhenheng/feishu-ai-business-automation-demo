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
from app.services.llm import generate_llm_report
from app.services.notifier import notify_all
from app.services.model_router import get_all_routes, select_model
from app.services.feishu_design import get_feishu_design

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
    return {
        "scene": "广州女装电商",
        "flow": [
            "客户下单",
            "店铺订单同步",
            "ERP订单池",
            "WMS库存校验",
            "物流发货跟踪",
            "客服售后处理",
            "财务回款对账",
            "AI日报与异常预警",
        ],
        "business_value": "把订单、库存、物流、客服、财务和日报串成闭环",
    }


@app.get("/api/mock/shop/orders")
def api_mock_shop_orders():
    return {
        "module": "店铺订单数据",
        "orders": [
            {
                "order_id": "SO-2026-001",
                "platform": "抖音小店",
                "shop_name": "华南服装旗舰店",
                "sku": "SKU-DRESS-BLK-M",
                "product_name": "黑色连衣裙 M码",
                "quantity": 2,
                "amount": 398,
                "status": "已付款",
                "created_at": "2026-06-26 10:12:00",
            },
            {
                "order_id": "SO-2026-002",
                "platform": "天猫店",
                "shop_name": "广州直播服饰店",
                "sku": "SKU-TSHIRT-WHT-L",
                "product_name": "白色T恤 L码",
                "quantity": 5,
                "amount": 495,
                "status": "待发货",
                "created_at": "2026-06-26 10:30:00",
            },
            {
                "order_id": "SO-2026-003",
                "platform": "拼多多店",
                "shop_name": "深圳跨境电商店",
                "sku": "SKU-SKIRT-KHA-M",
                "product_name": "卡其半身裙 M码",
                "quantity": 3,
                "amount": 357,
                "status": "待库存校验",
                "created_at": "2026-06-26 11:05:00",
            },
        ],
    }


@app.post("/api/mock/shop/orders/sync")
def api_mock_shop_orders_sync():
    return {
        "module": "店铺订单同步",
        "synced_count": 5,
        "exception_count": 1,
        "next_action": "写入ERP订单池，并触发WMS库存校验",
    }


@app.post("/api/mock/wms/inventory/check")
def api_mock_wms_inventory_check():
    return {
        "module": "WMS库存校验",
        "low_stock": [
            {
                "sku": "SKU-DRESS-BLK-M",
                "product": "黑色连衣裙 M码",
                "stock": 18,
                "safe_stock": 80,
                "gap": 62,
            },
            {
                "sku": "SKU-TSHIRT-WHT-L",
                "product": "白色T恤 L码",
                "stock": 40,
                "safe_stock": 120,
                "gap": 80,
            },
        ],
        "next_action": "生成库存预警，并推送飞书机器人",
    }


@app.post("/api/mock/logistics/track")
def api_mock_logistics_track():
    return {
        "module": "物流轨迹查询",
        "tracking_no": "YT20260626001",
        "status": "异常",
        "reason": "揽收后超过24小时未更新",
        "next_action": "通知客服跟进，并同步客户解释话术",
    }


@app.post("/api/mock/finance/reconcile")
def api_mock_finance_reconcile():
    return {
        "module": "财务对账",
        "order_amount": 23800,
        "received_amount": 22600,
        "difference": 1200,
        "reason": "退款、平台扣点、优惠券未同步",
        "next_action": "创建财务复核任务",
    }


@app.post("/api/mock/crm/leads")
def api_mock_crm_leads():
    return {
        "module": "CRM线索沉淀",
        "leads": [
            {
                "name": "刘女士",
                "source": "网站AI客服",
                "intent": "高",
                "status": "待跟进",
            },
            {
                "name": "张先生",
                "source": "企业微信咨询",
                "intent": "中",
                "status": "已记录",
            },
        ],
        "next_action": "高意向客户推送销售负责人",
    }


@app.get("/api/sql/examples")
def api_sql_examples():
    return {
        "module": "MySQL / SQL 能力展示",
        "examples": [
            {
                "title": "查询未关闭异常订单",
                "sql": "SELECT * FROM exceptions WHERE status <> '已关闭' ORDER BY priority DESC;",
                "value": "快速定位还没有处理完的业务异常",
            },
            {
                "title": "查询低库存 SKU",
                "sql": "SELECT sku, product_name, stock, safe_stock, safe_stock - stock AS gap FROM inventory WHERE stock < safe_stock;",
                "value": "用于触发补货提醒和采购审批",
            },
            {
                "title": "统计每日订单数和异常数",
                "sql": "SELECT DATE(created_at) AS day, COUNT(*) AS order_count, SUM(is_exception) AS exception_count FROM orders GROUP BY DATE(created_at);",
                "value": "用于生成每日AI业务日报",
            },
            {
                "title": "查询高意向客户线索",
                "sql": "SELECT * FROM customer_leads WHERE intent_level = '高' AND status = '待跟进';",
                "value": "用于分派销售或客服负责人",
            },
            {
                "title": "查询财务对账差异",
                "sql": "SELECT order_id, order_amount, received_amount, order_amount - received_amount AS diff FROM finance_reconcile WHERE order_amount <> received_amount;",
                "value": "用于财务复核和异常提醒",
            },
        ],
    }


@app.get("/api/ai/roadmap")
def api_ai_roadmap():
    return {
        "module": "AI / RAG / 预测模型路线",
        "roadmap": [
            {
                "name": "客服知识库RAG",
                "scene": "客服自动回复、售后规则查询、尺码推荐",
                "value": "降低重复咨询成本，提高回复一致性",
            },
            {
                "name": "订单异常摘要",
                "scene": "把库存不足、物流延迟、客户催单汇总成日报",
                "value": "让负责人快速知道今天最该处理什么",
            },
            {
                "name": "库存缺货预测",
                "scene": "根据销量、库存、安全库存预测未来缺口",
                "value": "提前补货，减少爆款断货",
            },
            {
                "name": "爆款 SKU 预测",
                "scene": "结合销售趋势、直播间数据、收藏加购数据识别潜力款",
                "value": "辅助运营和供应链备货",
            },
            {
                "name": "财务异常识别",
                "scene": "平台回款、退款、优惠券、扣点差异识别",
                "value": "减少人工对账压力",
            },
            {
                "name": "多模型路由",
                "scene": "日报用稳定模型，异常分类用低成本模型，客服用中文表达更好的模型",
                "value": "兼顾质量、成本、速度和隐私",
            },
        ],
    }


@app.get("/api/deployment/checklist")
def api_deployment_checklist():
    return {
        "module": "Linux / Docker 部署清单",
        "checklist": [
            "Ubuntu 服务环境准备",
            "Python venv 虚拟环境",
            ".env 环境变量配置",
            "Docker Compose 启动 app + mysql",
            "Nginx 反向代理 8000 端口",
            "systemd 配置服务常驻运行",
            "日志排查：uvicorn / nginx / application logs",
            "Webhook 安全配置：不要把机器人地址提交到 GitHub",
        ],
    }
