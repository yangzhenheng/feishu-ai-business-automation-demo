# AI Business FlowPilot｜飞书低代码供应链与客服自动化系统

> AI + 飞书低代码 + 企业微信/飞书机器人 + Webhook + CC Switch 多模型 API 路由 + AI 客服 + 供应链业务自动化作品集项目

这个项目用于求职展示、面试演示和 GitHub 作品集沉淀。项目定位不是算法研究，而是 **把 AI 工具接入企业真实业务流程**：把订单、库存、异常、客户咨询、日报、通知这些原本依赖 Excel、微信群、人工催办的流程，升级为可追踪、可自动提醒、可 AI 总结、可多模型路由的业务流程驾驶舱。

## 项目竞争力定位

这个项目重点证明 5 件事：

1. **懂飞书低代码落地**：不是只写代码，而是能设计多维表格、审批/自动化规则、Webhook 推送和业务闭环。
2. **懂业务流程拆解**：能把订单、库存、异常、客户线索、日报拆成清晰的数据对象和流程节点。
3. **懂 AI 工具接入业务**：AI 用于日报、异常分类、客户线索判断、处理建议，而不是只聊天。
4. **懂多模型 API 实践**：使用 CC Switch 思路做模型路由，根据任务选择 Claude/GPT/Qwen/DeepSeek/Kimi/本地模型等。
5. **能快速交付 MVP**：本地无 API Key 也可运行，有 API Key 可扩展到真实大模型和机器人通知。

## 适合展示的岗位方向

- AI 低代码实施 / 飞书低代码流程搭建
- AI 业务自动化 / 企业 AI 工具落地
- 供应链数字化 / 订单协同 / 运营效率工具
- AI 客服 / 企业微信机器人 / 飞书机器人
- 初级产品实施 / 业务流程自动化助理

## 一句话价值

> 用飞书多维表格承载业务数据，用自动化规则触发流程，用 Webhook 推送机器人，用 AI 生成日报和异常建议，用 CC Switch/多模型路由兼顾质量、速度、成本和隐私。

## 功能模块

### 1. 业务驾驶舱 Dashboard

- 订单总数
- 未关闭异常
- 库存预警
- 未完成待办
- 客户线索

### 2. 飞书低代码表结构设计

文档：[`docs/FEISHU_BITABLE_SCHEMA.md`](docs/FEISHU_BITABLE_SCHEMA.md)

设计 5 张核心表：

- 订单表 Orders
- 库存表 Inventory
- 异常表 Exceptions
- 客户线索表 Leads
- AI 日报表 Reports

### 3. 飞书自动化规则设计

文档：[`docs/FEISHU_AUTOMATION_WORKFLOWS.md`](docs/FEISHU_AUTOMATION_WORKFLOWS.md)

覆盖 8 条自动化规则：

- 库存低于安全库存 → 创建异常 + 推送库存预警
- 订单交期小于 3 天 → 提醒负责人
- 订单状态变为异常 → AI 分类 + 创建异常记录
- P0/P1 异常 → Webhook 推送飞书/企微群
- 异常超过 24 小时未关闭 → 升级提醒
- 客户高意向咨询 → 沉淀线索 + 推送负责人
- 每天 18:00 → 自动生成 AI 日报
- 不同 AI 任务 → 多模型路由

### 4. AI 异常分类

接口：`POST /api/ai/exception-classify`

输入：

```text
客户订单延期，库存不足，供应商还没确认发货，客户明天催单。
```

输出：

```text
异常类型：库存不足 / 供应商延迟
严重等级：P1
责任部门：采购 / 仓储 / 供应商管理
建议动作：优先确认可用库存和供应商补货交期，同时准备替代SKU方案。
```

### 5. AI 业务日报

接口：`GET /api/report/daily`

- 无 API Key：使用规则引擎生成稳定日报，保证面试现场可演示。
- 有 API Key：调用 OpenAI-Compatible API，对日报进行自然语言优化。

### 6. 飞书 / 企业微信机器人指令中心

接口：`POST /api/bot/command`

支持命令：

```text
/日报        生成今日业务日报
/异常        查看异常订单
/库存        查看库存预警
/客户线索    查看客户咨询线索
/待办        查看未完成事项
/帮助        查看命令说明
```

### 7. 24 小时 AI 客服 Demo

接口：`POST /api/customer-service`

- 自动回答服务项目、报价、交付流程、售后等问题
- 自动识别客户意向
- 自动生成客户需求摘要
- 自动沉淀到客户线索池
- 可扩展推送飞书/企业微信机器人

### 8. CC Switch 多模型 API 路由

文档：

- [`docs/CC_SWITCH_WORKFLOW.md`](docs/CC_SWITCH_WORKFLOW.md)
- [`docs/MULTI_MODEL_API_ROUTING.md`](docs/MULTI_MODEL_API_ROUTING.md)
- [`docs/MODEL_EVALUATION_REPORT.md`](docs/MODEL_EVALUATION_REPORT.md)

接口：

```text
GET  /api/model-routing
POST /api/model-routing/select
```

路由策略：

| 任务 | 主模型 | 备用模型 | 策略 |
|---|---|---|---|
| AI 业务日报 | Claude / GPT | Qwen / DeepSeek / Kimi | 正式输出优先质量 |
| 异常分类 | DeepSeek / Qwen | GLM / Kimi | 高频任务优先成本 |
| 客服回复 | Kimi / Qwen / GPT | Claude / DeepSeek | 中文表达优先 |
| 代码生成 | Claude / GPT / Qwen Coder | DeepSeek Coder | 编程能力优先 |
| 本地知识库 | Ollama / 本地模型 | Qwen / Kimi / GPT | 隐私和成本优先 |

### 9. Agent / Function Calling 设计

文档：[`docs/AI_AGENT_DESIGN.md`](docs/AI_AGENT_DESIGN.md)

设计 3 个业务 Agent：

- 异常分析 Agent
- 日报 Agent
- 客服线索 Agent

## 系统架构

```text
用户 / 业务人员 / 客户
        ↓
Web Dashboard / 网站AI客服 / 机器人命令
        ↓
FastAPI 服务层
        ├── 订单/库存/异常/线索业务逻辑
        ├── AI日报生成
        ├── AI异常分类
        ├── 多模型 API 路由
        └── 飞书/企业微信 Webhook 推送
        ↓
SQLite Demo 数据库 / 飞书多维表格设计
        ↓
飞书群 / 企业微信群 / 业务日报 / 待办闭环
```

## 项目结构

```text
feishu-ai-business-automation-demo/
├── app/
│   ├── main.py
│   ├── db.py
│   ├── services/
│   │   ├── business.py
│   │   ├── feishu_design.py
│   │   ├── llm.py
│   │   ├── model_router.py
│   │   └── notifier.py
│   └── static/
│       ├── index.html
│       ├── style.css
│       └── app.js
├── data/
│   ├── model_eval_samples.json
│   ├── sample_orders.csv
│   ├── sample_inventory.csv
│   └── sample_exceptions.csv
├── docs/
│   ├── AI_AGENT_DESIGN.md
│   ├── CC_SWITCH_WORKFLOW.md
│   ├── FEISHU_AUTOMATION_WORKFLOWS.md
│   ├── FEISHU_BITABLE_SCHEMA.md
│   ├── MODEL_EVALUATION_REPORT.md
│   ├── MULTI_MODEL_API_ROUTING.md
│   ├── PRODUCT_PRESENTATION.md
│   └── INTERVIEW_DEMO_SCRIPT.md
├── tests/
├── .env.example
├── requirements.txt
├── Dockerfile
└── README.md
```

## 快速启动

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

浏览器打开：

```text
http://127.0.0.1:8000
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

## 环境变量

本地演示可以不配置任何 Key。

```text
DATABASE_PATH=./business_demo.db
FEISHU_WEBHOOK_URL=
WECHAT_WORK_WEBHOOK_URL=
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

## GitHub 展示建议

1. 把本项目置顶到 GitHub 首页。
2. README 顶部放项目截图。
3. 面试前跑通本地 Demo，准备 Dashboard、AI日报、异常分类、模型路由、飞书表结构 5 张截图。
4. 简历项目链接写：`https://github.com/yangzhenheng/feishu-ai-business-automation-demo`

## 面试展示路径

1. 打开 Dashboard，展示订单、异常、库存、待办、客户线索指标。
2. 讲业务流程闭环：订单 → 库存校验 → 异常识别 → 待办/审批 → 机器人通知 → AI日报复盘。
3. 点击“生成日报”，展示 AI 日报。
4. 演示 `/异常`、`/库存`、`/客户线索` 命令。
5. 输入异常描述，展示 AI 异常分类和责任部门判断。
6. 展示 CC Switch 多模型路由：不同任务选择不同模型。
7. 打开飞书表结构和自动化规则文档，说明如何迁移到真实飞书。

## 简历项目名建议

**AI + 飞书低代码供应链协同与客服自动化系统**

项目描述可写为：

> 基于 FastAPI、SQLite、Webhook、飞书/企业微信机器人、CC Switch 多模型 API 路由和 LLM API，搭建 AI 业务自动化 Demo，实现订单管理、库存预警、异常分类、责任部门判断、AI 日报、机器人指令、24 小时 AI 客服和客户线索沉淀。项目模拟企业从 Excel/人工沟通向飞书低代码自动化系统迁移的流程，并设计多维表格 Schema、自动化规则、Agent/Function Calling 思路和模型路由策略。

## 后续扩展路线

- 接入真实飞书多维表格 API
- 接入飞书审批流
- 接入企业微信/飞书真实机器人 Webhook
- 增加 Excel 批量导入
- 增加 RAG 知识库客服
- 增加在线部署地址
- 增加权限系统和多角色流程
