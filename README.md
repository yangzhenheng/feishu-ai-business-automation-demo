# Feishu AI Business Automation Demo

> AI + 飞书低代码 + 企业微信/飞书机器人 + AI 客服 + 供应链业务自动化项目

这是一个用于求职展示、面试演示和 GitHub 作品集沉淀的项目。项目定位不是“算法研究”，而是 **AI 工具接入真实业务流程**：把订单、库存、异常、客户咨询、日报、通知这些原本依赖 Excel、微信群、人工催办的流程，做成可追踪、可自动提醒、可 AI 总结的业务自动化 Demo。

## 适合展示的岗位方向

- AI 低代码实施 / 飞书低代码流程搭建
- AI 业务自动化 / 企业 AI 工具落地
- 供应链数字化 / 订单协同 / 运营效率工具
- AI 客服 / 企业微信机器人 / 飞书机器人
- 初级产品实施 / 业务流程自动化助理

## 项目价值一句话

> 用飞书低代码、Webhook、企业微信/飞书机器人、基础 API 和 AI 总结能力，把企业内部的订单协同、库存预警、异常审批、客户咨询和日报汇总做成可运行的 MVP。

## 核心功能

### 1. 供应链订单协同系统

- 订单管理：客户、SKU、数量、交期、负责人、状态
- 库存管理：当前库存、安全库存、供应商、仓库位置
- 异常管理：库存不足、交期延误、质检异常、供应商延迟
- 待办管理：责任人、优先级、处理状态
- Dashboard：订单数、异常数、库存预警、待办数

### 2. AI 异常日报

- 自动统计今日订单、异常、库存风险、待办事项
- 支持两种模式：
  - 无 API Key：使用内置规则生成日报，保证本地可演示
  - 有 API Key：调用 OpenAI-Compatible API 生成更自然的业务日报

### 3. 飞书 / 企业微信机器人通知

- 支持飞书自定义机器人 Webhook
- 支持企业微信机器人 Webhook
- 可推送：日报、异常订单、库存预警、客户线索、待办提醒

### 4. 机器人指令中心

支持模拟以下命令：

```text
/日报        生成今日业务日报
/异常        查看异常订单
/库存        查看库存预警
/客户线索    查看客户咨询线索
/待办        查看未完成事项
/帮助        查看命令说明
```

### 5. 24 小时 AI 客服 Demo

- 自动回答服务项目、报价、交付流程、售后等问题
- 自动识别客户意向
- 生成客户线索
- 可推送到飞书/企业微信做跟进

## 项目结构

```text
feishu-ai-business-automation-demo/
├── app/
│   ├── main.py                  # FastAPI 入口
│   ├── db.py                    # SQLite 初始化与种子数据
│   ├── services/
│   │   ├── business.py           # 业务统计与规则
│   │   ├── llm.py                # AI 日报生成
│   │   └── notifier.py           # 飞书/企业微信通知
│   └── static/
│       ├── index.html            # 演示页面
│       ├── style.css
│       └── app.js
├── data/
│   ├── sample_orders.csv
│   ├── sample_inventory.csv
│   └── sample_exceptions.csv
├── docs/
│   ├── PROJECT_BRIEF.md          # 项目说明书
│   ├── AUTOMATION_RULES.md       # 自动化规则设计
│   ├── INTERVIEW_DEMO_SCRIPT.md  # 面试演示讲稿
│   └── GITHUB_PUSH_GUIDE.md      # GitHub 上传命令
├── tests/
│   └── test_business.py
├── .env.example
├── requirements.txt
├── Dockerfile
└── README.md
```

## 快速启动

### 1. 安装依赖

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

本地演示可以不配置任何 Key，系统会使用规则生成日报。

如需测试机器人通知，可在 `.env` 中填写：

```text
FEISHU_WEBHOOK_URL=你的飞书机器人 webhook
WECHAT_WORK_WEBHOOK_URL=你的企业微信机器人 webhook
```

如需接入 OpenAI-Compatible API，可填写：

```text
OPENAI_API_KEY=你的key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

### 3. 启动项目

```bash
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

## Docker 启动

```bash
docker build -t feishu-ai-business-automation-demo .
docker run --env-file .env -p 8000:8000 feishu-ai-business-automation-demo
```

## 面试展示建议

面试展示时，建议按这个顺序讲：

1. 先讲业务问题：Excel 分散、异常靠人催、客户线索无法沉淀、日报人工整理。
2. 再讲解决方案：用飞书多维表格承载数据，用自动化规则触发提醒，用机器人推送，用 AI 总结日报。
3. 打开 Dashboard 展示订单、库存、异常、待办、客户线索。
4. 点击生成日报，展示 AI 总结结果。
5. 演示 `/异常`、`/库存`、`/客户线索` 命令。
6. 说明如何接入真实飞书低代码系统和企业微信/飞书机器人。

## 项目亮点

- 不是单纯 AI 聊天，而是把 AI 接到业务流程里。
- 不是重型 ERP，而是低代码 MVP，适合快速验证。
- 同时覆盖供应链、客服、日报、机器人通知、业务看板。
- 本地无 Key 也能演示，面试稳定性更高。
- 代码结构清晰，适合上传 GitHub 作为作品集。

## 可继续扩展

- 接入飞书多维表格真实 API
- 接入飞书审批流
- 增加文件上传与 Excel 导入
- 增加 RAG 知识库客服
- 增加真实网站嵌入式客服组件
- 增加权限系统和账号登录
- 增加业务流程图 BPMN 展示

## 简历项目名建议

**AI + 飞书低代码供应链协同与客服自动化系统**

项目描述可写为：

> 基于 FastAPI、SQLite、Webhook、飞书/企业微信机器人和 LLM API，搭建 AI 业务自动化 Demo，实现订单管理、库存预警、异常跟进、AI 日报、机器人指令和 24 小时 AI 客服。项目模拟企业从 Excel/人工沟通向低代码自动化系统迁移的流程，可扩展接入飞书多维表格和审批流。
