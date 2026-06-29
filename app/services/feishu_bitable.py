from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List


REAL_REQUIRED_CONFIG = [
    "FEISHU_APP_ID",
    "FEISHU_APP_SECRET",
    "FEISHU_APP_TOKEN",
    "FEISHU_TABLE_ORDERS",
    "FEISHU_TABLE_INVENTORY",
    "FEISHU_TABLE_EXCEPTIONS",
    "FEISHU_TABLE_LEADS",
    "FEISHU_TABLE_REPORTS",
]


class FeishuBitableClient:
    """Feishu Bitable integration facade.

    The current implementation is intentionally mock-first. Real API mode is
    represented by configuration checks and a stable method boundary so the
    production HTTP calls can be added later without changing FastAPI routes.
    """

    module = "feishu_bitable"

    def __init__(self) -> None:
        self.enable_real_api = os.getenv("FEISHU_ENABLE_REAL_API", "false").lower() == "true"

    def missing_config(self) -> List[str]:
        return [key for key in REAL_REQUIRED_CONFIG if not os.getenv(key)]

    def config_complete(self) -> bool:
        return not self.missing_config()

    def current_mode(self) -> str:
        if self.enable_real_api and self.config_complete():
            return "real_ready"
        return "mock"

    def health_check(self) -> Dict[str, Any]:
        missing = self.missing_config()
        config_complete = not missing
        if self.enable_real_api and config_complete:
            message = "真实飞书配置已完整，当前处于 real_ready 预留模式。"
            next_action = "补充真实飞书多维表格 HTTP API 调用后即可切换为生产同步。"
            current_mode = "real_ready"
        elif self.enable_real_api:
            message = "真实飞书配置不完整，已自动降级到 Mock 模式。"
            next_action = "补齐 App ID、App Secret、App Token 和各 Table ID 后再启用真实同步。"
            current_mode = "mock"
        else:
            message = "当前使用 Mock 模式，可在无企业密钥的情况下完整演示业务同步。"
            next_action = "配置真实飞书开放平台参数并设置 FEISHU_ENABLE_REAL_API=true 后可进入 real_ready。"
            current_mode = "mock"
        return {
            "current_mode": current_mode,
            "enable_real_api": self.enable_real_api,
            "config_complete": config_complete,
            "missing_config": missing,
            "message": message,
            "next_action": next_action,
        }

    def _sync_result(self, action: str, target_table: str, records: Iterable[Dict[str, Any]], message: str) -> Dict[str, Any]:
        rows = list(records)
        health = self.health_check()
        mode = "mock"
        extra: Dict[str, Any] = {}
        if self.enable_real_api and self.config_complete():
            mode = "real_ready"
            message = f"Real 模式配置已就绪：{target_table} 同步接口预留完成，当前未发起真实飞书 API 请求。"
        elif self.enable_real_api and not self.config_complete():
            extra["missing_config"] = health["missing_config"]
            message = "真实飞书配置不完整，已自动降级到 Mock 模式。"

        return {
            "mode": mode,
            "ok": True,
            "module": self.module,
            "action": action,
            "message": message,
            "data": {
                "synced_records": len(rows),
                "target_table": target_table,
                "next_action": "配置真实 FEISHU_APP_ID、FEISHU_APP_SECRET、FEISHU_APP_TOKEN 和 TABLE_ID 后可切换真实 API",
            },
            **extra,
        }

    def sync_orders_to_bitable(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._sync_result("sync_orders", "orders", orders, "Mock 模式：订单数据已模拟同步到飞书多维表格")

    def sync_inventory_to_bitable(self, inventory: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._sync_result("sync_inventory", "inventory", inventory, "Mock 模式：库存数据已模拟同步到飞书多维表格")

    def sync_exceptions_to_bitable(self, exceptions: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._sync_result("sync_exceptions", "exceptions", exceptions, "Mock 模式：异常数据已模拟同步到飞书多维表格")

    def sync_leads_to_bitable(self, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._sync_result("sync_leads", "leads", leads, "Mock 模式：客户线索已模拟同步到飞书多维表格")

    def sync_report_to_bitable(self, report: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._sync_result("sync_report", "reports", report, "Mock 模式：AI日报已模拟同步到飞书多维表格")

    def sync_all_to_bitable(self, payload: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        results = [
            self.sync_orders_to_bitable(payload.get("orders", [])),
            self.sync_inventory_to_bitable(payload.get("inventory", [])),
            self.sync_exceptions_to_bitable(payload.get("exceptions", [])),
            self.sync_leads_to_bitable(payload.get("leads", [])),
            self.sync_report_to_bitable(payload.get("reports", [])),
        ]
        synced_records = sum(item["data"]["synced_records"] for item in results)
        synced_tables = ["orders", "inventory", "exceptions", "leads", "reports"]
        mode = "real_ready" if all(item["mode"] == "real_ready" for item in results) else "mock"
        message = "Mock 模式：订单、库存、异常、客户线索和AI日报已模拟同步到飞书多维表格"
        if mode == "real_ready":
            message = "Real 模式配置已就绪：全量同步接口预留完成，当前未发起真实飞书 API 请求。"
        response: Dict[str, Any] = {
            "mode": mode,
            "ok": True,
            "module": self.module,
            "action": "sync_all",
            "message": message,
            "synced_tables": synced_tables,
            "total_synced_records": synced_records,
            "results": results,
            "next_action": "配置真实 FEISHU_APP_ID、FEISHU_APP_SECRET、FEISHU_APP_TOKEN 和 TABLE_ID 后可切换真实 API",
            "data": {
                "synced_records": synced_records,
                "total_synced_records": synced_records,
                "target_table": "orders,inventory,exceptions,leads,reports",
                "synced_tables": synced_tables,
                "next_action": "配置真实 FEISHU_APP_ID、FEISHU_APP_SECRET、FEISHU_APP_TOKEN 和 TABLE_ID 后可切换真实 API",
                "results": results,
            },
        }
        if self.enable_real_api and not self.config_complete():
            response["missing_config"] = self.missing_config()
            response["message"] = "真实飞书配置不完整，已自动降级到 Mock 模式。"
        return response
