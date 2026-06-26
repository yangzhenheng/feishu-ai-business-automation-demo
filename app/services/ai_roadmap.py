from __future__ import annotations

from typing import Any, Dict, List


def get_ai_roadmap() -> Dict[str, List[Dict[str, str]]]:
    return {
        "roadmap": [
            {
                "name": "客服RAG",
                "scenario": "网站 AI 客服、直播间客服、飞书客服助手",
                "business_value": "基于商品、尺码、物流和售后知识库生成稳定回复。",
            },
            {
                "name": "售后知识库",
                "scenario": "退换货、少发漏发、尺码换货、补偿规则",
                "business_value": "把售后规则结构化，减少客服人工判断成本。",
            },
            {
                "name": "库存预测",
                "scenario": "广州仓、佛山仓 SKU 安全库存和补货周期预测",
                "business_value": "提前发现断码断色风险，触发采购补货审批。",
            },
            {
                "name": "爆款SKU预测",
                "scenario": "直播间订单、加购、转化率和活动排期分析",
                "business_value": "识别连衣裙、T恤、卫衣等爆款趋势，辅助备货。",
            },
            {
                "name": "财务异常识别",
                "scenario": "店铺账单、ERP订单、退款售后和平台扣点对账",
                "business_value": "自动定位回款差异并创建财务复核任务。",
            },
            {
                "name": "多模型路由",
                "scenario": "日报、异常分类、客服回复、私域知识库等不同任务",
                "business_value": "按质量、成本、延迟和隐私要求选择不同模型。",
            },
        ]
    }
