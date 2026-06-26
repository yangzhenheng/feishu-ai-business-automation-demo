from __future__ import annotations

from typing import Any, Dict, List


def get_ecommerce_flow() -> Dict[str, Any]:
    steps: List[Dict[str, str]] = [
        {
            "step": "客户下单",
            "owner": "店铺运营",
            "system": "抖音小店 / 天猫店 / 拼多多店",
            "output": "订单、SKU、买家备注、支付金额",
        },
        {
            "step": "店铺订单同步",
            "owner": "低代码开发工程师",
            "system": "店铺开放平台 API / 飞书云函数",
            "output": "标准化订单写入 ERP 订单池",
        },
        {
            "step": "ERP订单池",
            "owner": "运营 / 商品 / 客服",
            "system": "ERP / 飞书多维表格",
            "output": "订单状态、异常标签、负责人",
        },
        {
            "step": "WMS库存校验",
            "owner": "仓储",
            "system": "广州仓 / 佛山仓 WMS",
            "output": "可发库存、低库存 SKU、缺口数量",
        },
        {
            "step": "发货/物流跟踪",
            "owner": "仓储 / 物流专员",
            "system": "快递鸟 / 顺丰 / 中通 API",
            "output": "运单状态、延迟、退回、少发漏发风险",
        },
        {
            "step": "客服售后",
            "owner": "客服",
            "system": "CRM / 飞书任务 / RAG知识库",
            "output": "退换货处理、买家安抚话术、售后规则匹配",
        },
        {
            "step": "财务回款",
            "owner": "财务",
            "system": "店铺账单 / ERP / 财务系统",
            "output": "订单金额、已回款金额、差异原因",
        },
        {
            "step": "AI日报/异常预警",
            "owner": "管理层 / 各部门负责人",
            "system": "LLM / 多模型路由 / 飞书机器人",
            "output": "日报摘要、风险排序、审批和跟进动作",
        },
    ]
    return {
        "scene": "广州女装电商 ERP/WMS/CRM 低代码业务闭环",
        "flow_text": "客户下单 -> 店铺订单同步 -> ERP订单池 -> WMS库存校验 -> 发货/物流跟踪 -> 客服售后 -> 财务回款 -> AI日报/异常预警",
        "steps": steps,
        "low_code_value": [
            "用飞书多维表格承载轻量 ERP/WMS/CRM 数据对象",
            "用自动化和审批流把异常从发现推进到负责人处理",
            "用云函数对接店铺、物流、财务和 AI API",
            "用 RAG 和预测模型逐步提升客服、库存和财务效率",
        ],
    }


def get_deployment_checklist() -> Dict[str, Any]:
    return {
        "title": "Linux / Docker 部署清单",
        "items": [
            {"name": "Ubuntu 环境", "check": "Ubuntu 22.04/24.04，开放 8000/80/443 端口，配置普通运行用户"},
            {"name": "Python venv", "check": "python3 -m venv .venv && pip install -r requirements.txt"},
            {"name": ".env", "check": "配置 DATABASE_PATH、FEISHU_WEBHOOK_URL、OPENAI_API_KEY、OPENAI_BASE_URL"},
            {"name": "Docker Compose", "check": "app + mysql 服务编排，MySQL 初始化挂载 sql/init.sql"},
            {"name": "Nginx 反向代理", "check": "把公网域名转发到 127.0.0.1:8000，并启用 HTTPS"},
            {"name": "systemd 常驻运行", "check": "非 Docker 部署时用 systemd 管理 uvicorn/gunicorn 进程"},
            {"name": "日志排查", "check": "journalctl、docker logs、Nginx access/error log、应用异常日志"},
            {"name": "Webhook 安全配置", "check": "校验签名/Token、限制来源、避免把密钥写入代码仓库"},
        ],
    }
