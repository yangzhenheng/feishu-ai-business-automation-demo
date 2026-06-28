from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter

from app.db import get_connection
from app.services.notifier import notify_all

router = APIRouter()


def rows_to_dicts(rows) -> List[Dict[str, Any]]:
    return [dict(row) for row in rows]


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def request_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def query_rows(sql: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        return rows_to_dicts(conn.execute(sql).fetchall())
    finally:
        conn.close()


@router.get("/api/ecommerce/flow")
def api_ecommerce_flow():
    return {
        "scene": "广州女装电商 ERP/WMS/CRM 自动化",
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
        "business_value": "把订单、库存、物流、客服、财务和日报串成闭环，让负责人先看风险而不是翻表。",
    }


@router.get("/api/mock/shop/orders")
def api_mock_shop_orders():
    conn = get_connection()
    try:
        orders = rows_to_dicts(
            conn.execute(
                """
                SELECT order_no AS order_id, platform, shop_name, sku, product_name,
                       quantity, amount, status, created_at
                FROM orders
                ORDER BY created_at DESC
                LIMIT 5
                """
            ).fetchall()
        )
    finally:
        conn.close()
    return {"module": "店铺订单数据", "orders": orders}


@router.post("/api/mock/shop/orders/sync")
def api_mock_shop_orders_sync():
    orders = query_rows(
        """
        SELECT order_no, platform, shop_name, sku, product_name, quantity, amount, status
        FROM orders
        ORDER BY created_at DESC
        LIMIT 5
        """
    )
    exception_count = sum(1 for item in orders if item["status"] in ["物流异常", "待库存校验", "售后换码"])
    return {
        "module": "店铺订单同步",
        "status": "success",
        "request_id": request_id("SHOP"),
        "source_system": "抖音小店 / 天猫店 / 拼多多店",
        "result_summary": f"同步 {len(orders)} 条女装订单到 ERP 订单池，异常候选 {exception_count} 条。",
        "risk_points": ["直播间订单高峰可能造成重复同步", "售后换码和物流异常需要进入 ERP 异常池"],
        "next_actions": ["写入ERP订单池", "触发WMS库存校验", "对异常候选订单打标"],
        "orders": orders,
        "synced_count": len(orders),
        "exception_count": exception_count,
    }


@router.post("/api/mock/wms/inventory/check")
def api_mock_wms_inventory_check():
    low_stock = query_rows(
        """
        SELECT sku, product_name AS product, current_stock AS stock,
               safety_stock AS safe_stock, safety_stock - current_stock AS gap,
               warehouse, supplier
        FROM inventory
        WHERE current_stock < safety_stock
        ORDER BY gap DESC
        """
    )
    return {
        "module": "WMS库存校验",
        "status": "warning" if low_stock else "success",
        "request_id": request_id("WMS"),
        "source_system": "广州仓 / 佛山仓 WMS",
        "result_summary": f"完成库存校验，发现 {len(low_stock)} 个低库存 SKU。",
        "risk_points": [f"{item['sku']} 缺口 {item['gap']} 件" for item in low_stock] or ["暂无低库存风险"],
        "next_actions": ["生成库存预警", "推送飞书机器人", "触发采购补货审批"],
        "low_stock": low_stock,
    }


@router.post("/api/mock/logistics/track")
def api_mock_logistics_track():
    return {
        "module": "物流轨迹查询",
        "status": "warning",
        "request_id": request_id("LOG"),
        "source_system": "圆通/中通物流轨迹 API",
        "result_summary": "运单 YT20260626001 揽收后超过24小时未更新，已识别为物流异常。",
        "risk_points": ["客户已催单", "若继续无轨迹可能产生差评或退款"],
        "next_actions": ["通知客服跟进", "同步客户解释话术", "必要时升级物流供应商"],
        "tracking_no": "YT20260626001",
        "logistics_status": "异常",
        "reason": "揽收后超过24小时未更新",
    }


@router.post("/api/mock/finance/reconcile")
def api_mock_finance_reconcile():
    rows = query_rows(
        """
        SELECT order_no, platform, order_amount, received_amount, difference, reason, status
        FROM finance_reconcile
        WHERE ABS(difference) > 0
        ORDER BY ABS(difference) DESC
        """
    )
    total_diff = sum(float(item["difference"]) for item in rows)
    return {
        "module": "财务对账",
        "status": "warning" if rows else "success",
        "request_id": request_id("FIN"),
        "source_system": "店铺平台账单 / 财务回款表",
        "result_summary": f"发现 {len(rows)} 笔回款差异，差异金额合计 {total_diff:.2f} 元。",
        "risk_points": [f"{item['order_no']}：{item['reason']}，差异 {item['difference']} 元" for item in rows] or ["暂无差异"],
        "next_actions": ["创建财务复核任务", "核对优惠券/平台扣点/退款状态", "复核后回写财务表"],
        "differences": rows,
        "difference": total_diff,
    }


@router.post("/api/mock/crm/leads")
def api_mock_crm_leads():
    leads = query_rows(
        """
        SELECT name, source, intent_level AS intent, status, owner, demand
        FROM customer_leads
        ORDER BY CASE intent_level WHEN '高' THEN 1 WHEN '中' THEN 2 ELSE 3 END, created_at DESC
        LIMIT 5
        """
    )
    high_count = sum(1 for item in leads if item["intent"] == "高")
    return {
        "module": "CRM线索沉淀",
        "status": "success",
        "request_id": request_id("CRM"),
        "source_system": "网站AI客服 / 企业微信咨询 / 抖音小店客服",
        "result_summary": f"沉淀 {len(leads)} 条客户线索，其中 {high_count} 条高意向。",
        "risk_points": ["高意向客户若未及时跟进，可能流失到竞品店铺"],
        "next_actions": ["高意向客户推送销售负责人", "记录跟进状态", "沉淀到客户线索表"],
        "leads": leads,
    }


@router.get("/api/sql/examples")
def api_sql_examples():
    examples = [
        {
            "title": "查询未关闭异常订单",
            "description": "定位仍需供应链、客服或仓储继续处理的异常单。",
            "sql": """
                SELECT exception_no, order_no, exception_type, priority, status, owner
                FROM exceptions
                WHERE status <> '已关闭'
                ORDER BY CASE priority WHEN '高' THEN 1 WHEN '中' THEN 2 ELSE 3 END, created_at DESC;
            """,
        },
        {
            "title": "查询低库存 SKU",
            "description": "识别低于安全库存的 SKU，支撑采购补货审批。",
            "sql": """
                SELECT sku, product_name, current_stock, safety_stock,
                       safety_stock - current_stock AS gap, warehouse
                FROM inventory
                WHERE current_stock < safety_stock
                ORDER BY gap DESC;
            """,
        },
        {
            "title": "统计每日订单数和异常数",
            "description": "用于 AI 日报的订单总量、异常量趋势统计。",
            "sql": """
                SELECT DATE(created_at) AS day,
                       COUNT(*) AS order_count,
                       SUM(is_exception) AS exception_count,
                       ROUND(SUM(amount), 2) AS order_amount
                FROM orders
                GROUP BY DATE(created_at)
                ORDER BY day DESC;
            """,
        },
        {
            "title": "查询高意向客户线索",
            "description": "将高意向客户推送给销售负责人或客服主管。",
            "sql": """
                SELECT name, source, demand, intent_level, status, owner
                FROM customer_leads
                WHERE intent_level = '高'
                ORDER BY created_at DESC;
            """,
        },
        {
            "title": "查询财务对账差异",
            "description": "识别平台扣点、优惠券、退款导致的回款差异。",
            "sql": """
                SELECT order_no, platform, order_amount, received_amount,
                       difference, reason, status
                FROM finance_reconcile
                WHERE ABS(difference) > 0
                ORDER BY ABS(difference) DESC;
            """,
        },
    ]

    conn = get_connection()
    try:
        for item in examples:
            item["sql"] = " ".join(item["sql"].split())
            item["rows"] = rows_to_dicts(conn.execute(item["sql"]).fetchall())
    finally:
        conn.close()
    return {"module": "SQLite / SQL 能力展示", "examples": examples}


@router.get("/api/ai/roadmap")
def api_ai_roadmap():
    return {
        "module": "AI / RAG / 预测模型路线",
        "roadmap": [
            {"name": "客服知识库RAG", "scene": "客服自动回复、售后规则查询、尺码推荐", "value": "降低重复咨询成本，提高回复一致性"},
            {"name": "订单异常摘要", "scene": "库存不足、物流延迟、客户催单自动汇总", "value": "让负责人快速知道今天最该处理什么"},
            {"name": "库存缺货预测", "scene": "根据销量、库存、安全库存预测未来缺口", "value": "提前补货，减少爆款断货"},
            {"name": "爆款 SKU 预测", "scene": "结合直播间、收藏加购、销量趋势识别潜力款", "value": "辅助运营和供应链备货"},
            {"name": "财务异常识别", "scene": "平台回款、退款、优惠券、扣点差异识别", "value": "减少人工对账压力"},
            {"name": "多模型路由", "scene": "按日报、分类、客服、知识库选择不同模型", "value": "兼顾质量、成本、速度和隐私"},
        ],
    }


@router.get("/api/deployment/checklist")
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


def build_full_flow_result() -> Dict[str, Any]:
    low_stock = query_rows(
        """
        SELECT sku, product_name AS product, current_stock AS stock,
               safety_stock AS safe_stock, safety_stock - current_stock AS gap
        FROM inventory
        WHERE current_stock < safety_stock
        ORDER BY gap DESC
        """
    )
    finance_rows = query_rows("SELECT * FROM finance_reconcile WHERE ABS(difference) > 0")
    lead_rows = query_rows("SELECT * FROM customer_leads ORDER BY created_at DESC")
    ai_report = (
        f"【AI业务日报】今日订单总数 5，未关闭异常 4，库存预警 {len(low_stock)}，客户线索 {len(lead_rows)}。"
        "优先处理 EXP-001 库存不足、EXP-002 交期风险，并安排客服跟进高意向客户和财务复核差异订单。"
    )
    return {
        "title": "女装电商 AI 业务闭环演示",
        "scene": "广州女装电商 ERP/WMS/CRM 自动化",
        "steps": [
            {"step": 1, "name": "店铺订单同步", "status": "success", "detail": "从抖音小店、天猫店、拼多多店同步 5 条订单", "business_value": "减少运营手工导表和漏单风险"},
            {"step": 2, "name": "ERP订单池入库", "status": "success", "detail": "订单写入 ERP 订单池，统一订单状态、负责人和异常标签", "business_value": "形成跨平台订单统一入口"},
            {"step": 3, "name": "WMS库存校验", "status": "warning", "detail": f"发现 {len(low_stock)} 个低库存 SKU", "business_value": "提前识别缺货和断码风险", "data": low_stock},
            {"step": 4, "name": "异常单生成", "status": "warning", "detail": "自动生成库存不足、交期风险、物流延迟等异常单", "business_value": "让异常进入闭环处理而不是散落在聊天记录"},
            {"step": 5, "name": "飞书机器人通知", "status": "success", "detail": "通过 Webhook 推送 AI 日报和异常摘要到测试群", "business_value": "负责人在飞书群直接看到风险"},
            {"step": 6, "name": "CRM客户线索沉淀", "status": "success", "detail": f"识别 {len(lead_rows)} 条客户线索，其中高意向线索可分派销售", "business_value": "把客服咨询转成可跟进商机"},
            {"step": 7, "name": "财务回款对账", "status": "warning", "detail": f"发现 {len(finance_rows)} 笔回款差异，建议财务复核", "business_value": "减少平台账单和实收金额差异遗漏"},
            {"step": 8, "name": "AI日报生成", "status": "success", "detail": "生成今日订单、库存、异常、客户线索和财务风险日报", "business_value": "让负责人每天先看异常和建议动作"},
        ],
        "ai_report": ai_report,
        "business_value": [
            "把店铺订单、ERP、WMS、物流、客服、财务和AI日报串成闭环",
            "减少人工查表、人工催单、人工日报整理",
            "让负责人每天先看异常和风险，而不是从大量表格里找问题",
        ],
    }


def build_feishu_push_detail(feishu_push: str, ai_report: str) -> Dict[str, str]:
    message_summary = ai_report.split("。", 1)[0] + "。"
    base = {
        "platform": "飞书",
        "group": "AI业务自动化Demo测试群",
        "time": now_text(),
        "message_summary": message_summary,
    }
    if feishu_push == "success":
        return {**base, "status": "success", "title": "推送成功", "reason": "Webhook 已返回成功响应", "next_action": "负责人可在群内继续跟进异常单和财务复核"}
    if feishu_push.startswith("skipped"):
        return {**base, "status": "skipped", "title": "推送跳过", "reason": "FEISHU_WEBHOOK_URL is empty", "next_action": "在 .env 配置 FEISHU_WEBHOOK_URL 后重新运行演示"}
    return {**base, "status": "failed", "title": "推送失败", "reason": feishu_push.replace("failed:", "").strip() or "飞书机器人接口未返回成功状态", "next_action": "检查 Webhook 地址、网络连通性和机器人权限"}


@router.post("/api/demo/run-full-flow")
def api_demo_run_full_flow():
    result = build_full_flow_result()
    if not os.getenv("FEISHU_WEBHOOK_URL"):
        result["feishu_push"] = "skipped: FEISHU_WEBHOOK_URL is empty"
    else:
        try:
            notify_result = notify_all(result["ai_report"])
            result["feishu_push"] = "success" if notify_result.get("feishu", {}).get("ok") else "failed"
            result["feishu_notify_detail"] = notify_result.get("feishu")
        except Exception as exc:
            result["feishu_push"] = f"failed: {exc}"

    result["feishu_push_detail"] = build_feishu_push_detail(result["feishu_push"], result["ai_report"])
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO workflow_logs(workflow_name, trigger_type, status, executed_at, summary, pushed_to_feishu, next_action)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "女装电商AI业务闭环",
                "manual_demo",
                "success",
                now_text(),
                "同步订单5条，异常4条，库存预警已生成，AI日报已生成",
                result["feishu_push_detail"]["status"],
                result["feishu_push_detail"]["next_action"],
            ),
        )
        conn.execute(
            "INSERT INTO ai_reports(report_type, content, model_route, created_at) VALUES (?, ?, ?, ?)",
            ("daily", result["ai_report"], "daily_report", now_text()),
        )
        conn.commit()
    finally:
        conn.close()
    return result


@router.get("/api/workflow/logs")
def api_workflow_logs():
    conn = get_connection()
    try:
        logs = rows_to_dicts(
            conn.execute(
                """
                SELECT workflow_name, trigger_type, status, executed_at, summary, pushed_to_feishu, next_action
                FROM workflow_logs
                ORDER BY id DESC
                LIMIT 10
                """
            ).fetchall()
        )
    finally:
        conn.close()
    for log in logs:
        log["workflow"] = log["workflow_name"]
        log["trigger"] = log["trigger_type"]
        log["time"] = log["executed_at"]
    return logs
