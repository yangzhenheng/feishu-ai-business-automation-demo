from __future__ import annotations

from typing import Any, Dict, List


def get_sql_examples() -> Dict[str, List[Dict[str, Any]]]:
    return {
        "examples": [
            {
                "title": "查询未关闭异常订单",
                "business_value": "给运营负责人查看当天仍需处理的 P0/P1 风险。",
                "sql": "SELECT exception_no, order_id, exception_type, priority, owner, status FROM exceptions WHERE status <> '已关闭' ORDER BY priority DESC, created_at DESC;",
            },
            {
                "title": "查询低库存 SKU",
                "business_value": "给采购和仓储触发补货审批。",
                "sql": "SELECT sku, product_name, warehouse, available_stock, safety_stock, (safety_stock - available_stock) AS gap_quantity FROM inventory WHERE available_stock < safety_stock ORDER BY gap_quantity DESC;",
            },
            {
                "title": "统计每日订单数和异常数",
                "business_value": "支撑 AI 日报中的经营概览和异常趋势。",
                "sql": "SELECT DATE(o.created_at) AS biz_date, COUNT(*) AS order_count, SUM(CASE WHEN e.id IS NULL THEN 0 ELSE 1 END) AS exception_count FROM orders o LEFT JOIN exceptions e ON o.order_id = e.order_id GROUP BY DATE(o.created_at) ORDER BY biz_date DESC;",
            },
            {
                "title": "查询高意向客户线索",
                "business_value": "把直播间、售后和私域咨询沉淀成 CRM 跟进任务。",
                "sql": "SELECT lead_id, customer_name, source, intent_level, follow_status, recommended_owner FROM customer_leads WHERE intent_level = '高' AND follow_status <> '已成交' ORDER BY created_at DESC;",
            },
            {
                "title": "查询财务对账差异",
                "business_value": "定位退款、平台扣点、优惠券和少结算导致的回款差异。",
                "sql": "SELECT reconcile_id, order_id, order_amount, received_amount, diff_amount, diff_reason, status FROM finance_reconcile WHERE diff_amount <> 0 ORDER BY ABS(diff_amount) DESC;",
            },
        ]
    }
