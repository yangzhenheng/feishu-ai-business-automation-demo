from __future__ import annotations

from typing import Any, Dict, List

BITABLE_SCHEMA: List[Dict[str, Any]] = [
    {
        "table_name": "订单表 Orders",
        "purpose": "承载客户订单、SKU、交期、负责人、状态，是供应链协同的主数据表。",
        "fields": [
            {"name": "订单编号", "type": "文本", "example": "SO-2026-001"},
            {"name": "客户名称", "type": "文本", "example": "华南服装旗舰店"},
            {"name": "SKU", "type": "文本/关联库存", "example": "SKU-HOODIE-GRY-L"},
            {"name": "数量", "type": "数字", "example": 120},
            {"name": "交期", "type": "日期", "example": "2026-06-27"},
            {"name": "负责人", "type": "人员", "example": "李强"},
            {"name": "订单状态", "type": "单选", "example": "待确认/生产中/异常/待发货/已完成"},
            {"name": "是否异常", "type": "公式/复选", "example": "库存不足或交期小于3天自动标记"},
        ],
    },
    {
        "table_name": "库存表 Inventory",
        "purpose": "管理SKU库存、安全库存、供应商和仓库，作为库存预警和补货动作的数据源。",
        "fields": [
            {"name": "SKU", "type": "文本", "example": "SKU-HOODIE-GRY-L"},
            {"name": "商品名称", "type": "文本", "example": "灰色卫衣 L码"},
            {"name": "当前库存", "type": "数字", "example": 40},
            {"name": "安全库存", "type": "数字", "example": 120},
            {"name": "库存缺口", "type": "公式", "example": "安全库存-当前库存"},
            {"name": "供应商", "type": "文本", "example": "供应商B"},
            {"name": "预警状态", "type": "单选/公式", "example": "正常/低库存/缺货"},
        ],
    },
    {
        "table_name": "异常表 Exceptions",
        "purpose": "沉淀库存不足、交期风险、信息缺失、质检异常等问题，形成异常闭环。",
        "fields": [
            {"name": "异常编号", "type": "文本", "example": "EXP-001"},
            {"name": "关联订单", "type": "关联记录", "example": "SO-2026-002"},
            {"name": "异常类型", "type": "单选", "example": "库存不足/交期风险/信息缺失/质检异常"},
            {"name": "严重等级", "type": "单选", "example": "P0/P1/P2/P3"},
            {"name": "责任部门", "type": "单选", "example": "采购/仓储/客服/供应商/质检"},
            {"name": "处理状态", "type": "单选", "example": "待处理/处理中/待客户确认/已关闭"},
            {"name": "AI建议", "type": "长文本", "example": "优先确认供应商补货交期，并同步客户延期风险。"},
        ],
    },
    {
        "table_name": "客户线索表 Leads",
        "purpose": "承接网站AI客服/表单/企业微信咨询，沉淀客户需求与跟进状态。",
        "fields": [
            {"name": "客户姓名", "type": "文本", "example": "张先生"},
            {"name": "联系方式", "type": "文本", "example": "wechat: zhang-demo"},
            {"name": "需求摘要", "type": "长文本", "example": "咨询网站AI客服和自动报价功能"},
            {"name": "意向等级", "type": "单选", "example": "高/中/低"},
            {"name": "来源", "type": "单选", "example": "网站AI客服/表单/企微"},
            {"name": "跟进状态", "type": "单选", "example": "待跟进/已联系/已完成"},
        ],
    },
    {
        "table_name": "AI日报表 Reports",
        "purpose": "保存每日AI业务日报，形成管理层复盘和跨部门协作记录。",
        "fields": [
            {"name": "日期", "type": "日期", "example": "2026-06-26"},
            {"name": "日报正文", "type": "长文本", "example": "订单总数、异常数、重点风险、次日行动"},
            {"name": "模型来源", "type": "单选", "example": "规则版/Claude/GPT/Qwen/DeepSeek"},
            {"name": "推送状态", "type": "单选", "example": "未推送/已推送飞书/已推送企微"},
        ],
    },
]

WORKFLOWS: List[Dict[str, str]] = [
    {"name": "库存预警", "trigger": "库存表：当前库存 < 安全库存", "action": "自动生成异常记录，推送 /库存 到飞书群，创建采购补货待办", "business_value": "减少人工查库存，提前暴露缺货风险"},
    {"name": "订单交期风险", "trigger": "订单表：交期小于3天且状态未完成", "action": "提醒负责人，必要时升级给供应链/客服负责人", "business_value": "降低临期未发货导致的客户投诉"},
    {"name": "异常订单闭环", "trigger": "订单状态变为异常", "action": "创建异常表记录，调用AI生成分类、等级、责任部门和处理建议", "business_value": "把模糊问题变成可追踪记录"},
    {"name": "P0/P1升级提醒", "trigger": "异常等级为P0或P1", "action": "通过Webhook推送飞书/企微群，并创建高优先级待办", "business_value": "高风险问题快速同步到相关人"},
    {"name": "超时未处理升级", "trigger": "异常创建超过24小时仍未关闭", "action": "升级提醒owner和部门负责人", "business_value": "避免异常记录沉底"},
    {"name": "客户线索沉淀", "trigger": "AI客服识别到中/高意向客户", "action": "写入客户线索表，推送销售/负责人跟进", "business_value": "避免客户咨询流失"},
    {"name": "每日AI日报", "trigger": "每天18:00定时", "action": "汇总订单、库存、异常、待办、线索，生成日报并推送", "business_value": "替代人工统计日报，形成管理复盘"},
    {"name": "模型路由", "trigger": "不同AI任务被调用", "action": "按任务类型选择主模型和备用模型，兼顾质量、速度、成本", "business_value": "避免所有任务都用昂贵模型，提高落地性"},
]


def get_feishu_design() -> Dict[str, Any]:
    return {
        "positioning": "把飞书多维表格作为轻量业务数据库，把审批/自动化/Webhook作为流程引擎，把AI作为异常分析和日报总结层。",
        "tables": BITABLE_SCHEMA,
        "workflows": WORKFLOWS,
    }
