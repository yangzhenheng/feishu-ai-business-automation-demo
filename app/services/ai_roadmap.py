from __future__ import annotations

from typing import Any, Dict, List


def get_ai_roadmap() -> Dict[str, List[Dict[str, str]]]:
    return {
        "roadmap": [
            {
                "module": "客服知识库 RAG",
                "data_source": "商品详情、尺码表、售后规则、物流话术、历史客服问答",
                "business_value": "提升直播间和店铺客服回复一致性，减少新人培训成本。",
                "phase": "V3 设计，V4 可接入向量库",
            },
            {
                "module": "订单异常摘要",
                "data_source": "订单池、异常表、物流轨迹、买家备注",
                "business_value": "自动生成异常原因、责任部门和下一步动作。",
                "phase": "V3 已用规则模拟，后续接 LLM Function Calling",
            },
            {
                "module": "库存缺货预测",
                "data_source": "库存、销量、活动日历、直播排期、补货周期",
                "business_value": "提前识别断码断色风险，触发采购补货审批。",
                "phase": "V3 路线设计，后续接 Prophet/XGBoost/LightGBM",
            },
            {
                "module": "爆款 SKU 预警",
                "data_source": "店铺订单、点击转化、加购、直播间成交曲线",
                "business_value": "发现连衣裙、T恤、卫衣等爆发款，联动备货和投放。",
                "phase": "V3 路线设计",
            },
            {
                "module": "财务对账异常识别",
                "data_source": "店铺账单、ERP订单、退款售后、平台扣点",
                "business_value": "自动定位少结算、退款延迟、优惠券承担差异。",
                "phase": "V3 模拟 API",
            },
            {
                "module": "多模型路由策略",
                "data_source": "任务类型、成本、延迟、隐私等级、质量要求",
                "business_value": "日报走高质量模型，分类走低成本模型，私域知识走本地或私有模型。",
                "phase": "V2 已有 CC Switch 说明，V3 扩展到电商场景",
            },
        ]
    }
