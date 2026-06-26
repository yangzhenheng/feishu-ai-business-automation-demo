from __future__ import annotations

from typing import Any, Dict


def get_ecommerce_flow() -> Dict[str, Any]:
    return {
        "scene": "广州女装电商",
        "flow": [
            "客户下单",
            "店铺订单同步",
            "ERP订单池",
            "WMS库存校验",
            "物流发货跟踪",
            "客服售后处理",
            "财务回款对账",
            "AI日报与异常预警",
        ],
        "business_value": "把订单、库存、物流、客服、财务和日报串成闭环",
    }


def get_deployment_checklist() -> Dict[str, Any]:
    return {
        "module": "Linux/Docker部署清单",
        "checklist": [
            {"name": "Ubuntu", "value": "Ubuntu 22.04/24.04，开放 8000/80/443 端口"},
            {"name": "Python venv", "value": "python3 -m venv .venv && pip install -r requirements.txt"},
            {"name": "Docker Compose", "value": "app + mysql 编排，挂载 sql/init.sql 初始化数据库"},
            {"name": "Nginx", "value": "配置反向代理到 127.0.0.1:8000，并启用 HTTPS"},
            {"name": "systemd", "value": "非 Docker 部署时保持 Uvicorn/Gunicorn 常驻运行"},
            {"name": ".env", "value": "配置 Webhook、OpenAI-Compatible API、数据库连接等密钥"},
            {"name": "Webhook安全配置", "value": "校验签名/Token，避免密钥进入 Git 仓库"},
            {"name": "日志排查", "value": "使用 journalctl、docker logs、Nginx 日志和应用日志定位问题"},
        ],
    }
