# CC Switch 多模型 API 调用工作流

本项目把 CC Switch 作为多模型 API 配置与切换的实践背景，用于展示对 Claude Code、Codex、Gemini、OpenAI-Compatible API 以及多 Provider 配置的理解。

## 为什么加入 CC Switch

企业 AI 落地不是永远调用一个模型。不同任务对质量、成本、速度、隐私要求不同：

- 业务日报：需要表达稳定、逻辑完整。
- 异常分类：需要结构化输出、低成本、高频调用。
- 中文客服：需要中文自然表达和需求追问。
- 代码生成：需要上下文能力和代码质量。
- 内部 SOP 问答：可能需要本地模型或私有化方案。

## 工具链定位

```text
CC Switch
  ├── 管理 Provider / API Key / Base URL / 模型名
  ├── 服务 Claude Code / Codex / Gemini 等 AI 编程工具
  ├── 支持 OpenAI-Compatible API
  ├── 支持按任务切换模型
  └── 支持测试不同模型在业务任务中的效果
```

## 任务型模型选择策略

| 任务 | 主模型 | 备用模型 | 选择逻辑 |
|---|---|---|---|
| AI 业务日报 | Claude / GPT | Qwen / DeepSeek / Kimi | 正式输出优先质量 |
| 异常分类 | DeepSeek / Qwen | GLM / Kimi | 高频任务优先成本和结构化稳定 |
| 客服回复 | Kimi / Qwen / GPT | Claude / DeepSeek | 中文表达和需求追问优先 |
| 代码生成 | Claude / GPT / Qwen Coder | DeepSeek Coder | 代码能力和上下文稳定优先 |
| 本地知识库 | Ollama / 本地模型 | Qwen / Kimi / GPT | 内部资料优先隐私与成本 |

## 项目中的体现

项目新增了 `app/services/model_router.py`，实现任务型模型路由 Demo：

- `/api/model-routing`：查看整体模型路由策略。
- `/api/model-routing/select`：按任务选择模型。
- `/api/ai/exception-classify`：异常分类时返回模型路由建议。

## 面试表达

> 我平时不只是调用单一模型，而是用 CC Switch 这类工具管理不同 Provider、API Key、Base URL 和模型配置。我的思路是按任务选模型：日报重质量，异常分类重成本和结构化，客服重中文表达，代码生成重代码能力，内部知识库重隐私和本地化。这个项目里我也做了一个简化版模型路由器，展示这种落地思路。
