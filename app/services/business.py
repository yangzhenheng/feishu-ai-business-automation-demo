from __future__ import annotations

import sqlite3
from typing import Any, Dict, List


def rows_to_dicts(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    return [dict(row) for row in rows]


def get_dashboard(conn: sqlite3.Connection) -> Dict[str, Any]:
    order_count = conn.execute("SELECT COUNT(*) AS c FROM orders").fetchone()["c"]
    exception_count = conn.execute("SELECT COUNT(*) AS c FROM exceptions WHERE status != '已关闭'").fetchone()["c"]
    low_stock_count = conn.execute(
        "SELECT COUNT(*) AS c FROM inventory WHERE current_stock < safety_stock"
    ).fetchone()["c"]
    todo_count = conn.execute("SELECT COUNT(*) AS c FROM todos WHERE status != '已完成'").fetchone()["c"]
    lead_count = conn.execute("SELECT COUNT(*) AS c FROM customer_leads WHERE status != '已完成'").fetchone()["c"]

    exceptions = rows_to_dicts(
        conn.execute(
            """
            SELECT exception_no, order_no, exception_type, reason, owner, priority, status
            FROM exceptions
            WHERE status != '已关闭'
            ORDER BY CASE priority WHEN '高' THEN 1 WHEN '中' THEN 2 ELSE 3 END, id DESC
            """
        ).fetchall()
    )
    low_stock = rows_to_dicts(
        conn.execute(
            """
            SELECT sku, product_name, current_stock, safety_stock, supplier, warehouse
            FROM inventory
            WHERE current_stock < safety_stock
            ORDER BY (safety_stock - current_stock) DESC
            """
        ).fetchall()
    )
    todos = rows_to_dicts(
        conn.execute(
            """
            SELECT title, owner, priority, status, due_date
            FROM todos
            WHERE status != '已完成'
            ORDER BY CASE priority WHEN '高' THEN 1 WHEN '中' THEN 2 ELSE 3 END, due_date ASC
            """
        ).fetchall()
    )
    leads = rows_to_dicts(
        conn.execute(
            """
            SELECT name, contact, demand, intent_level, source, status, created_at
            FROM customer_leads
            ORDER BY id DESC
            LIMIT 10
            """
        ).fetchall()
    )

    return {
        "metrics": {
            "orders": order_count,
            "active_exceptions": exception_count,
            "low_stock": low_stock_count,
            "open_todos": todo_count,
            "open_leads": lead_count,
        },
        "exceptions": exceptions,
        "low_stock": low_stock,
        "todos": todos,
        "leads": leads,
    }


def build_rule_based_report(conn: sqlite3.Connection) -> str:
    dashboard = get_dashboard(conn)
    metrics = dashboard["metrics"]
    exceptions = dashboard["exceptions"]
    low_stock = dashboard["low_stock"]
    todos = dashboard["todos"]
    leads = dashboard["leads"]

    lines = [
        "# 今日AI业务日报",
        "",
        f"## 1. 总览",
        f"- 今日订单总数：{metrics['orders']} 单",
        f"- 未关闭异常：{metrics['active_exceptions']} 项",
        f"- 库存预警 SKU：{metrics['low_stock']} 个",
        f"- 未完成待办：{metrics['open_todos']} 项",
        f"- 待跟进客户线索：{metrics['open_leads']} 条",
        "",
        "## 2. 重点风险",
    ]

    if exceptions:
        for exp in exceptions[:5]:
            lines.append(
                f"- [{exp['priority']}] {exp['exception_type']}：{exp['order_no']}，负责人 {exp['owner']}，原因：{exp['reason']}"
            )
    else:
        lines.append("- 暂无未关闭异常。")

    lines += ["", "## 3. 库存预警"]
    if low_stock:
        for item in low_stock:
            gap = item["safety_stock"] - item["current_stock"]
            lines.append(
                f"- {item['sku']} / {item['product_name']}：当前 {item['current_stock']}，安全库存 {item['safety_stock']}，缺口 {gap}，供应商 {item['supplier']}。"
            )
    else:
        lines.append("- 暂无低库存 SKU。")

    lines += ["", "## 4. 今日优先处理事项"]
    if todos:
        for todo in todos[:5]:
            lines.append(
                f"- [{todo['priority']}] {todo['title']}，负责人 {todo['owner']}，截止 {todo['due_date']}。"
            )
    else:
        lines.append("- 暂无未完成待办。")

    lines += ["", "## 5. 客户线索"]
    if leads:
        for lead in leads[:5]:
            lines.append(
                f"- {lead['name']}（{lead['intent_level']}意向）：{lead['demand']}，来源：{lead['source']}。"
            )
    else:
        lines.append("- 暂无新客户线索。")

    lines += [
        "",
        "## 6. AI处理建议",
        "- 优先关闭高优先级异常，尤其是库存不足和交期风险。",
        "- 对低库存 SKU 立即确认供应商补货周期，避免影响订单交付。",
        "- 将客户线索同步给销售或负责人，并记录下一步跟进时间。",
        "- 每日固定输出日报，形成异常闭环和跨部门协同记录。",
    ]
    return "\n".join(lines)


def command_response(conn: sqlite3.Connection, command: str) -> str:
    dashboard = get_dashboard(conn)
    command = command.strip()

    if command in ["/日报", "日报", "/report"]:
        return build_rule_based_report(conn)
    if command in ["/异常", "异常", "/exceptions"]:
        if not dashboard["exceptions"]:
            return "当前没有未关闭异常。"
        return "\n".join(
            [
                f"{e['exception_no']} | {e['order_no']} | {e['exception_type']} | {e['priority']} | {e['owner']} | {e['status']}"
                for e in dashboard["exceptions"]
            ]
        )
    if command in ["/库存", "库存", "/stock"]:
        if not dashboard["low_stock"]:
            return "当前没有低库存预警。"
        return "\n".join(
            [
                f"{i['sku']} | {i['product_name']} | 当前 {i['current_stock']} / 安全 {i['safety_stock']} | {i['supplier']}"
                for i in dashboard["low_stock"]
            ]
        )
    if command in ["/客户线索", "客户线索", "/leads"]:
        if not dashboard["leads"]:
            return "当前没有客户线索。"
        return "\n".join(
            [f"{l['name']} | {l['intent_level']}意向 | {l['demand']} | {l['contact'] or '未留联系方式'}" for l in dashboard["leads"]]
        )
    if command in ["/待办", "待办", "/todo"]:
        if not dashboard["todos"]:
            return "当前没有未完成待办。"
        return "\n".join(
            [f"{t['title']} | {t['priority']} | {t['owner']} | {t['due_date']} | {t['status']}" for t in dashboard["todos"]]
        )
    return "支持命令：/日报、/异常、/库存、/客户线索、/待办、/帮助"


def customer_service_answer(message: str) -> Dict[str, str]:
    text = message.lower()
    if any(k in text for k in ["价格", "报价", "多少钱", "費用", "费用", "quote"]):
        return {
            "answer": "我们可以先按需求复杂度报价：基础AI客服/FAQ整理适合低成本试跑；如果需要接入网站、飞书/企业微信通知、客户线索表和日报，需要按功能模块报价。建议先做一个MVP。",
            "intent_level": "高",
            "demand": "咨询报价与AI客服/自动化服务",
        }
    if any(k in text for k in ["网站", "客服", "24小时", "咨询", "自动回复"]):
        return {
            "answer": "可以做网站AI客服：先整理服务项目、常见问题、交付流程和售后说明，再接入网站入口，客户咨询后自动生成线索并推送到飞书或企业微信。",
            "intent_level": "高",
            "demand": "网站AI客服与客户线索收集",
        }
    if any(k in text for k in ["飞书", "企業微信", "企业微信", "机器人", "webhook"]):
        return {
            "answer": "可以接飞书/企业微信机器人，通过Webhook把客户咨询、异常订单、库存预警、日报等内容自动推送到群里，也可以设计 /日报、/异常、/库存 等命令。",
            "intent_level": "中",
            "demand": "飞书/企业微信机器人自动化通知",
        }
    return {
        "answer": "我可以先记录你的需求，并建议从一个小型MVP开始：明确业务流程、设计表结构、配置自动提醒，再用AI生成日报或客服回复。你可以补充你的业务场景、客户来源和希望自动化的环节。",
        "intent_level": "中",
        "demand": message[:80],
    }


def classify_exception_text(text: str) -> Dict[str, str]:
    """Rule-based AI-style exception classifier for stable local demo.

    In a real deployment this function can be replaced by an LLM Function Calling output.
    """
    raw = text.strip()
    lower = raw.lower()
    exception_type = "信息缺失"
    department = "业务/客服"
    severity = "P2"
    next_action = "补齐关键信息，确认负责人和截止时间。"

    if any(k in raw for k in ["库存", "缺货", "补货", "安全库存", "供应商未发"]):
        exception_type = "库存不足 / 供应商延迟"
        department = "采购 / 仓储 / 供应商管理"
        severity = "P1"
        next_action = "优先确认可用库存和供应商补货交期，同时准备替代SKU方案。"
    if any(k in raw for k in ["延期", "交期", "催单", "来不及", "超时"]):
        exception_type = "交期风险"
        department = "供应链 / 运营 / 客服"
        severity = "P1" if severity != "P0" else severity
        next_action = "同步客户预期，确认最晚发货时间，并升级负责人跟进。"
    if any(k in raw for k in ["质检", "不良", "返工", "瑕疵", "抽检"]):
        exception_type = "质检异常"
        department = "质检 / 生产 / 供应商"
        severity = "P0" if any(k in raw for k in ["批量", "大面积", "严重"]) else "P1"
        next_action = "立即隔离异常批次，复核不良比例，确认返工或替换方案。"
    if any(k in raw for k in ["客户没确认", "尺码", "颜色", "地址", "资料缺失", "信息缺失"]):
        exception_type = "客户信息缺失"
        department = "客服 / 销售"
        severity = "P2"
        next_action = "由客服确认缺失信息，超过约定时间未回复则标记交期风险。"
    if any(k in lower for k in ["p0", "urgent", "紧急", "重大", "停发", "无法发货"]):
        severity = "P0"

    return {
        "input": raw,
        "exception_type": exception_type,
        "severity": severity,
        "priority": severity,
        "owner_department": department,
        "suggested_action": next_action,
        "next_action": next_action,
        "structured_output": f"异常类型：{exception_type}\n严重等级：{severity}\n责任部门：{department}\n建议动作：{next_action}",
    }
