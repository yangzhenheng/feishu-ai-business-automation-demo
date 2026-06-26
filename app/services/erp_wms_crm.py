from __future__ import annotations

from typing import Any, Dict, List


def get_shop_orders() -> List[Dict[str, Any]]:
    return [
        {
            "order_id": "ORDER-20260626-001",
            "platform": "抖音小店",
            "shop_name": "广州女装直播间",
            "sku": "SKU-DRESS-BLK-M",
            "product_name": "黑色连衣裙 M码",
            "quantity": 2,
            "amount": 598,
            "status": "已支付",
            "created_at": "2026-06-26 10:18:00",
        },
        {
            "order_id": "ORDER-20260626-002",
            "platform": "天猫",
            "shop_name": "夏季通勤女装旗舰店",
            "sku": "SKU-TSHIRT-WHT-L",
            "product_name": "白色T恤 L码",
            "quantity": 5,
            "amount": 445,
            "status": "待发货",
            "created_at": "2026-06-26 10:42:00",
        },
        {
            "order_id": "ORDER-20260626-003",
            "platform": "拼多多",
            "shop_name": "广州女装清仓店",
            "sku": "SKU-SKIRT-DENIM-S",
            "product_name": "牛仔半身裙 S码",
            "quantity": 1,
            "amount": 89,
            "status": "待客服确认",
            "created_at": "2026-06-26 11:05:00",
        },
        {
            "order_id": "ORDER-20260626-004",
            "platform": "抖音小店",
            "shop_name": "广州女装直播间",
            "sku": "SKU-HOODIE-GRY-L",
            "product_name": "灰色卫衣 L码",
            "quantity": 8,
            "amount": 1192,
            "status": "急单",
            "created_at": "2026-06-26 11:26:00",
        },
        {
            "order_id": "ORDER-20260626-005",
            "platform": "天猫",
            "shop_name": "夏季通勤女装旗舰店",
            "sku": "SKU-DRESS-FLORAL-M",
            "product_name": "碎花连衣裙 M码",
            "quantity": 1,
            "amount": 229,
            "status": "售后换码",
            "created_at": "2026-06-26 11:48:00",
        },
    ]


def sync_shop_orders() -> Dict[str, Any]:
    return {
        "module": "店铺订单同步",
        "synced_count": 5,
        "exception_count": 1,
        "next_action": "写入ERP订单池，并触发库存校验",
    }


def check_inventory() -> Dict[str, Any]:
    return {
        "module": "WMS库存校验",
        "low_stock": [
            {"sku": "SKU-DRESS-BLK-M", "product": "黑色连衣裙 M码", "stock": 18, "safe_stock": 80, "gap": 62},
            {"sku": "SKU-TSHIRT-WHT-L", "product": "白色T恤 L码", "stock": 40, "safe_stock": 120, "gap": 80},
        ],
        "next_action": "生成库存预警并推送飞书机器人",
    }


def track_logistics() -> Dict[str, Any]:
    return {
        "module": "物流轨迹查询",
        "tracking_no": "YT20260626001",
        "status": "异常",
        "reason": "揽收后超过24小时未更新",
        "next_action": "通知客服跟进并同步客户解释话术",
    }


def reconcile_finance() -> Dict[str, Any]:
    return {
        "module": "财务对账",
        "order_amount": 23800,
        "received_amount": 22600,
        "difference": 1200,
        "reason": "退款/平台扣点/优惠券未同步",
        "next_action": "创建财务复核任务",
    }


def collect_crm_leads() -> Dict[str, Any]:
    return {
        "module": "CRM线索沉淀",
        "leads": [
            {"name": "刘女士", "source": "网站AI客服", "intent": "高", "status": "待跟进"},
            {"name": "张先生", "source": "企业微信咨询", "intent": "中", "status": "已记录"},
        ],
        "next_action": "高意向客户推送销售负责人",
    }
