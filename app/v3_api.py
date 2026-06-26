from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter

from app.services.notifier import notify_all

router = APIRouter()

LOW_STOCK_ITEMS = [
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
]

WORKFLOW_LOGS: List[Dict[str, str]] = [
    {
        "time": "2026-06-26 16:30:00",
        "workflow": "女装电商AI业务闭环",
        "trigger": "manual_demo",
        "status": "success",
        "summary": "同步订单5条，异常3条，库存预警2条，AI日报已生成",
    }
]


@router.get("/api/ecommerce/flow")
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


@router.get("/api/mock/shop/orders")
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
                "shop_name": "广州女装清仓店",
                "sku": "SKU-SKIRT-KHA-M",
                "product_name": "卡其半身裙 M码",
                "quantity": 3,
                "amount": 357,
                "status": "待库存校验",
                "created_at": "2026-06-26 11:05:00",
            },
            {
                "order_id": "SO-2026-004",
                "platform": "抖音小店",
                "shop_name": "广州女装直播间",
                "sku": "SKU-HOODIE-GRY-L",
                "product_name": "灰色短款卫衣 L码",
                "quantity": 1,
                "amount": 199,
                "status": "物流异常",
                "created_at": "2026-06-26 11:22:00",
            },
            {
                "order_id": "SO-2026-005",
                "platform": "天猫店",
                "shop_name": "广州直播服饰店",
                "sku": "SKU-DRESS-FLORAL-S",
                "product_name": "碎花连衣裙 S码",
                "quantity": 2,
                "amount": 438,
                "status": "售后换码",
                "created_at": "2026-06-26 11:48:00",
            },
        ],
    }


@router.post("/api/mock/shop/orders/sync")
def api_mock_shop_orders_sync():
    return {
        "module": "店铺订单同步",
        "core_result": "从抖音小店、天猫店、拼多多店同步 5 条订单",
        "risk": "发现 1 条订单存在物流或售后异常，需要进入 ERP 异常池",
        "synced_count": 5,
        "exception_count": 1,
        "next_action": "写入ERP订单池，并触发WMS库存校验",
    }


@router.post("/api/mock/wms/inventory/check")
def api_mock_wms_inventory_check():
    return {
        "module": "WMS库存校验",
        "core_result": "完成广州仓、佛山仓库存校验，发现 2 个低库存 SKU",
        "risk": "黑色连衣裙 M码和白色T恤 L码低于安全库存，存在断码和延迟发货风险",
        "low_stock": LOW_STOCK_ITEMS,
        "next_action": "生成库存预警并推送飞书机器人",
    }


@router.post("/api/mock/logistics/track")
def api_mock_logistics_track():
    return {
        "module": "物流轨迹查询",
        "core_result": "查询运单 YT20260626001，当前状态为异常",
        "risk": "揽收后超过24小时未更新，可能引发客户催单和差评",
        "tracking_no": "YT20260626001",
        "status": "异常",
        "reason": "揽收后超过24小时未更新",
        "next_action": "通知客服跟进并同步客户解释话术",
    }


@router.post("/api/mock/finance/reconcile")
def api_mock_finance_reconcile():
    return {
        "module": "财务对账",
        "core_result": "订单金额 23800 元，已回款 22600 元",
        "risk": "发现回款差异 1200 元，可能来自退款、平台扣点或优惠券未同步",
        "order_amount": 23800,
        "received_amount": 22600,
        "difference": 1200,
        "reason": "退款/平台扣点/优惠券未同步",
        "next_action": "创建财务复核任务",
    }


@router.post("/api/mock/crm/leads")
def api_mock_crm_leads():
    return {
        "module": "CRM线索沉淀",
        "core_result": "沉淀 2 条客户线索，其中 1 条高意向",
        "risk": "高意向客户如果未及时跟进，可能流失到竞品店铺",
        "leads": [
            {"name": "刘女士", "source": "网站AI客服", "intent": "高", "status": "待跟进"},
            {"name": "张先生", "source": "企业微信咨询", "intent": "中", "status": "已记录"},
        ],
        "next_action": "高意向客户推送销售负责人",
    }


@router.get("/api/sql/examples")
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


@router.get("/api/ai/roadmap")
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
    ai_report = (
        "【AI业务日报】今日订单总数 5，未关闭异常 3，库存预警 2，客户线索 4。"
        "优先处理 EXP-001 库存不足、EXP-002 交期风险，并安排客服跟进高意向客户。"
    )
    return {
        "title": "女装电商 AI 业务闭环演示",
        "scene": "广州女装电商 ERP/WMS/CRM 自动化",
        "steps": [
            {
                "step": 1,
                "name": "店铺订单同步",
                "status": "success",
                "summary": "从抖音小店、天猫店、拼多多店同步 5 条订单",
                "data": {"synced_count": 5, "exception_count": 1},
            },
            {
                "step": 2,
                "name": "ERP订单池入库",
                "status": "success",
                "summary": "订单写入 ERP 订单池，等待库存校验",
            },
            {
                "step": 3,
                "name": "WMS库存校验",
                "status": "warning",
                "summary": "发现 2 个低库存 SKU",
                "data": LOW_STOCK_ITEMS,
            },
            {
                "step": 4,
                "name": "异常单生成",
                "status": "warning",
                "summary": "自动生成库存不足异常 EXP-001，交期风险异常 EXP-002",
            },
            {
                "step": 5,
                "name": "飞书机器人通知",
                "status": "success",
                "summary": "通过 Webhook 推送异常摘要到飞书测试群",
            },
            {
                "step": 6,
                "name": "CRM客户线索沉淀",
                "status": "success",
                "summary": "识别 2 条客户线索，其中 1 条高意向",
            },
            {
                "step": 7,
                "name": "财务回款对账",
                "status": "warning",
                "summary": "发现回款差异 1200 元，建议财务复核",
            },
            {
                "step": 8,
                "name": "AI日报生成",
                "status": "success",
                "summary": "生成今日订单、库存、异常、客户线索和财务风险日报",
            },
        ],
        "ai_report": ai_report,
        "business_value": [
            "把店铺订单、ERP、WMS、物流、客服、财务和AI日报串成闭环",
            "减少人工查表、人工催单、人工日报整理",
            "让负责人每天先看异常和风险，而不是从大量表格里找问题",
        ],
    }


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

    WORKFLOW_LOGS.insert(
        0,
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "workflow": "女装电商AI业务闭环",
            "trigger": "manual_demo",
            "status": "success",
            "summary": "同步订单5条，异常3条，库存预警2条，AI日报已生成",
        },
    )
    del WORKFLOW_LOGS[10:]
    return result


@router.get("/api/workflow/logs")
def api_workflow_logs():
    return WORKFLOW_LOGS
