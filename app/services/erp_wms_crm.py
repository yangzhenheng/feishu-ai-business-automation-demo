from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _load_json(filename: str) -> Any:
    return json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))


def get_shop_orders() -> List[Dict[str, Any]]:
    return _load_json("sample_shop_orders.json")


def sync_shop_orders() -> Dict[str, Any]:
    orders = get_shop_orders()
    abnormal = [
        order
        for order in orders
        if order["order_status"] in {"售后中", "待客服确认"} or "换货" in order["buyer_note"] or "急" in order["buyer_note"]
    ]
    return {
        "source": "抖音小店 / 天猫店 / 拼多多店模拟同步",
        "synced_count": len(orders),
        "exception_count": len(abnormal),
        "erp_order_pool_status": "已写入 ERP 订单池，等待库存和物流校验",
        "next_action": [
            "将售后中、买家备注包含急单/换货的订单标记为异常",
            "触发 WMS 库存校验",
            "P1 异常推送飞书审批或负责人任务",
        ],
        "exception_orders": [order["order_id"] for order in abnormal],
    }


def check_inventory() -> Dict[str, Any]:
    inventory = _load_json("sample_wms_inventory.json")
    low_stock = []
    for item in inventory:
        gap = max(item["safety_stock"] - item["available_stock"], 0)
        if gap > 0:
            low_stock.append(
                {
                    "sku": item["sku"],
                    "product_name": item["product_name"],
                    "warehouse": item["warehouse"],
                    "available_stock": item["available_stock"],
                    "safety_stock": item["safety_stock"],
                    "gap_quantity": gap,
                    "suggested_action": "创建采购补货审批，并同步运营调整推广节奏",
                }
            )
    return {
        "checked_count": len(inventory),
        "low_stock_count": len(low_stock),
        "low_stock_skus": low_stock,
        "next_action": "低库存 SKU 进入飞书审批流：采购确认补货 -> 仓储确认到货 -> 运营调整商品投放。",
    }


def track_logistics() -> Dict[str, Any]:
    records = _load_json("sample_logistics.json")
    abnormal = [item for item in records if item["is_exception"]]
    return {
        "tracking_count": len(records),
        "exception_count": len(abnormal),
        "records": records,
        "next_action": "物流延迟、退回、少发漏发订单推送客服安抚，并升级仓储/物流专员处理。",
    }


def reconcile_finance() -> Dict[str, Any]:
    rows = _load_json("sample_finance_reconcile.json")
    total_order_amount = round(sum(row["order_amount"] for row in rows), 2)
    total_received_amount = round(sum(row["received_amount"] for row in rows), 2)
    total_diff = round(total_order_amount - total_received_amount, 2)
    abnormal = [row for row in rows if row["diff_amount"] != 0]
    return {
        "order_amount": total_order_amount,
        "received_amount": total_received_amount,
        "diff_amount": total_diff,
        "diff_count": len(abnormal),
        "diff_reasons": [row["diff_reason"] for row in abnormal],
        "records": rows,
        "suggested_action": "差异单进入财务复核审批，确认平台扣点、退款、优惠券和少结算原因。",
    }


def collect_crm_leads() -> Dict[str, Any]:
    leads = _load_json("sample_crm_leads.json")
    high_intent = [lead for lead in leads if lead["intent_level"] == "高"]
    return {
        "lead_count": len(leads),
        "high_intent_count": len(high_intent),
        "leads": leads,
        "next_action": "高意向客户自动创建销售跟进任务，中意向客户进入私域运营池。",
    }
