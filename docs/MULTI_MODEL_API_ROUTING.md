# 多模型 API 路由设计

## 设计目标

让 AI 不只是“调用一个接口”，而是根据业务任务自动选择合适模型，形成可解释、可扩展、可控制成本的企业 AI 调用策略。

## 路由原则

1. **正式输出优先质量**：日报、管理层汇报等场景优先 Claude/GPT。
2. **高频任务优先成本**：异常分类、标签提取、线索打分优先 DeepSeek/Qwen。
3. **中文客服优先表达**：中文客服和需求追问优先 Kimi/Qwen/GPT。
4. **代码任务优先编程能力**：接口、脚本、前端组件优先 Claude/GPT/Qwen Coder。
5. **内部资料优先隐私**：企业 SOP、客户资料、本地知识库优先本地模型或私有化方案。

## 项目接口

```http
GET /api/model-routing
POST /api/model-routing/select
POST /api/ai/exception-classify
```

## 示例输出

```json
{
  "task_type": "exception_classification",
  "task_name": "异常分类与责任部门判断",
  "primary_model": "DeepSeek / Qwen",
  "fallback_model": "GLM / Kimi",
  "quality_target": "结构化输出稳定，能识别异常类型、等级和责任部门",
  "cost_strategy": "高频批量任务优先低成本模型",
  "reason": "异常分类偏结构化和批量处理，重点是成本、速度和稳定格式。"
}
```

## 简历表达

> 使用 CC Switch 管理多模型 API 配置，围绕 AI 日报、异常分类、客服回复、代码生成、本地知识库等任务设计模型路由策略，根据质量、速度、成本和隐私要求选择主模型与备用模型。
