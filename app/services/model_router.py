from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Any


@dataclass
class ModelRoute:
    task_type: str
    task_name: str
    primary_model: str
    fallback_model: str
    quality_target: str
    cost_strategy: str
    reason: str
    privacy_strategy: str


ROUTES: Dict[str, ModelRoute] = {
    "daily_report": ModelRoute(
        task_type="daily_report",
        task_name="AI业务日报",
        primary_model="Claude / GPT",
        fallback_model="Qwen / DeepSeek / Kimi",
        quality_target="结构完整、表达专业、能给出可执行建议",
        cost_strategy="正式日报优先质量，批量日报可切低成本模型",
        reason="日报需要逻辑完整和表达稳定，优先使用综合能力强的模型。",
        privacy_strategy="日报只发送汇总指标和异常摘要，避免暴露客户联系方式。",
    ),
    "exception_classification": ModelRoute(
        task_type="exception_classification",
        task_name="异常分类与责任部门判断",
        primary_model="DeepSeek / Qwen",
        fallback_model="GLM / Kimi",
        quality_target="结构化输出稳定，能识别异常类型、等级和责任部门",
        cost_strategy="高频批量任务优先低成本模型",
        reason="异常分类偏结构化和批量处理，重点是成本、速度和稳定格式。",
        privacy_strategy="只传异常描述和订单号，不传客户手机号、地址等敏感字段。",
    ),
    "customer_service": ModelRoute(
        task_type="customer_service",
        task_name="AI客服回复与客户线索判断",
        primary_model="Kimi / Qwen / GPT",
        fallback_model="Claude / DeepSeek",
        quality_target="中文表达自然，能识别意向并沉淀需求",
        cost_strategy="高意向客户可用更强模型，普通FAQ用低成本模型",
        reason="客服场景需要中文表达、需求追问和线索识别。",
        privacy_strategy="客户联系方式入库前脱敏展示，私域客户资料优先走企业内部模型。",
    ),
    "code_generation": ModelRoute(
        task_type="code_generation",
        task_name="代码生成与低代码脚本辅助",
        primary_model="Claude / GPT / Qwen Coder",
        fallback_model="DeepSeek Coder",
        quality_target="代码可读、可运行、具备错误处理",
        cost_strategy="复杂代码用强模型，简单脚本用低成本模型",
        reason="代码任务优先选择编程能力强、上下文稳定的模型。",
        privacy_strategy="不上传真实密钥、Webhook 地址、数据库密码和客户数据。",
    ),
    "private_knowledge": ModelRoute(
        task_type="private_knowledge",
        task_name="本地知识库/SOP问答",
        primary_model="Ollama / 本地模型",
        fallback_model="Qwen / Kimi / GPT",
        quality_target="可在隐私场景下回答内部SOP和流程问题",
        cost_strategy="内部资料优先本地模型，公开资料可用云端模型",
        reason="企业内部SOP、客户资料和流程文档需要兼顾数据安全。",
        privacy_strategy="优先本地向量库和本地模型，外部模型只处理脱敏后的公开知识。",
    ),
}


EVALUATION_MATRIX: List[Dict[str, Any]] = [
    {"task": "业务日报", "model_family": "Claude / GPT", "quality": 9, "speed": 7, "cost": "高", "best_for": "正式日报、管理层汇报、复杂总结"},
    {"task": "异常分类", "model_family": "DeepSeek / Qwen", "quality": 8, "speed": 8, "cost": "低-中", "best_for": "批量结构化分类、风险打标、责任部门判断"},
    {"task": "中文客服", "model_family": "Kimi / Qwen / GPT", "quality": 8, "speed": 8, "cost": "中", "best_for": "客户咨询、需求追问、线索摘要"},
    {"task": "代码生成", "model_family": "Claude / GPT / Qwen Coder", "quality": 9, "speed": 7, "cost": "中-高", "best_for": "接口代码、自动化脚本、README和技术文档"},
    {"task": "本地SOP问答", "model_family": "Ollama / 本地模型", "quality": 6, "speed": 6, "cost": "低", "best_for": "内部资料、隐私数据、离线演示"},
]


def select_model(task_type: str) -> Dict[str, Any]:
    route = ROUTES.get(task_type, ROUTES["daily_report"])
    return asdict(route)


def get_all_routes() -> Dict[str, Any]:
    return {
        "strategy": "按任务类型做模型路由：正式输出优先质量，高频任务优先成本，内部资料优先本地/私有化。",
        "routes": [asdict(route) for route in ROUTES.values()],
        "evaluation_matrix": EVALUATION_MATRIX,
        "cc_switch_positioning": "使用 CC Switch 管理多 Provider / API Key / Base URL / 模型切换，服务 Claude Code、Codex、Gemini 等AI编程与工作流工具。",
    }
