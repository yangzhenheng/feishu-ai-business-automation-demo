import os
import sqlite3
from pathlib import Path
from typing import Iterable, Tuple

from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DATABASE_PATH", "./business_demo.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def execute_many(conn: sqlite3.Connection, sql: str, rows: Iterable[Tuple]) -> None:
    conn.executemany(sql, rows)
    conn.commit()


def init_db() -> None:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no TEXT UNIQUE NOT NULL,
            platform TEXT NOT NULL DEFAULT '抖音小店',
            shop_name TEXT NOT NULL DEFAULT '广州女装直播间',
            customer TEXT NOT NULL,
            sku TEXT NOT NULL,
            product_name TEXT NOT NULL DEFAULT '',
            quantity INTEGER NOT NULL,
            amount REAL NOT NULL DEFAULT 0,
            is_exception INTEGER NOT NULL DEFAULT 0,
            due_date TEXT NOT NULL,
            owner TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    ensure_columns(
        conn,
        "orders",
        {
            "platform": "TEXT NOT NULL DEFAULT '抖音小店'",
            "shop_name": "TEXT NOT NULL DEFAULT '广州女装直播间'",
            "product_name": "TEXT NOT NULL DEFAULT ''",
            "amount": "REAL NOT NULL DEFAULT 0",
            "is_exception": "INTEGER NOT NULL DEFAULT 0",
        },
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            product_name TEXT NOT NULL,
            current_stock INTEGER NOT NULL,
            safety_stock INTEGER NOT NULL,
            supplier TEXT NOT NULL,
            warehouse TEXT NOT NULL,
            updated_at TEXT NOT NULL DEFAULT ''
        )
        """
    )
    ensure_columns(conn, "inventory", {"updated_at": "TEXT NOT NULL DEFAULT ''"})

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS exceptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exception_no TEXT UNIQUE NOT NULL,
            order_no TEXT NOT NULL,
            exception_type TEXT NOT NULL,
            reason TEXT NOT NULL,
            owner TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS customer_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            demand TEXT NOT NULL,
            intent_level TEXT NOT NULL,
            source TEXT NOT NULL,
            status TEXT NOT NULL,
            owner TEXT NOT NULL DEFAULT '销售负责人',
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT,
            demand TEXT NOT NULL,
            intent_level TEXT NOT NULL,
            source TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            owner TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            due_date TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS finance_reconcile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no TEXT UNIQUE NOT NULL,
            platform TEXT NOT NULL,
            order_amount REAL NOT NULL,
            received_amount REAL NOT NULL,
            difference REAL NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL,
            owner TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ai_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_type TEXT NOT NULL,
            content TEXT NOT NULL,
            model_route TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS workflow_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow_name TEXT NOT NULL,
            trigger_type TEXT NOT NULL,
            status TEXT NOT NULL,
            executed_at TEXT NOT NULL,
            summary TEXT NOT NULL,
            pushed_to_feishu TEXT NOT NULL,
            next_action TEXT NOT NULL
        )
        """
    )

    conn.commit()
    seed_db(conn)
    conn.close()


def ensure_columns(conn: sqlite3.Connection, table: str, columns: dict[str, str]) -> None:
    existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    for name, definition in columns.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")
    conn.commit()


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]


def seed_db(conn: sqlite3.Connection) -> None:
    execute_many(
        conn,
        """
        INSERT OR REPLACE INTO orders(
            order_no, platform, shop_name, customer, sku, product_name, quantity,
            amount, is_exception, due_date, owner, status, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            ("SO-2026-001", "抖音小店", "广州女装直播间", "刘女士", "SKU-DRESS-BLK-M", "黑色连衣裙 M码", 2, 398, 1, "2026-06-27", "陈静", "待库存校验", "2026-06-27 09:20:00"),
            ("SO-2026-002", "天猫店", "广州直播服饰店", "张女士", "SKU-TSHIRT-WHT-L", "白色T恤 L码", 5, 495, 1, "2026-06-27", "李强", "待发货", "2026-06-27 09:45:00"),
            ("SO-2026-003", "拼多多店", "广州女装清仓店", "王女士", "SKU-SKIRT-KHA-M", "卡其半身裙 M码", 3, 357, 0, "2026-06-28", "赵敏", "已入ERP订单池", "2026-06-27 10:12:00"),
            ("SO-2026-004", "抖音小店", "华南服装旗舰店", "周女士", "SKU-HOODIE-GRY-L", "灰色短款卫衣 L码", 1, 199, 1, "2026-06-27", "陈静", "物流异常", "2026-06-27 10:35:00"),
            ("SO-2026-005", "天猫店", "广州直播服饰店", "林女士", "SKU-DRESS-FLORAL-S", "碎花连衣裙 S码", 2, 438, 0, "2026-06-29", "李强", "售后换码", "2026-06-27 11:08:00"),
        ],
    )

    execute_many(
        conn,
        """
        INSERT OR REPLACE INTO inventory(sku, product_name, current_stock, safety_stock, supplier, warehouse, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            ("SKU-DRESS-BLK-M", "黑色连衣裙 M码", 18, 80, "番禺连衣裙工厂", "广州仓", "2026-06-27 09:00:00"),
            ("SKU-TSHIRT-WHT-L", "白色T恤 L码", 40, 120, "白云针织供应商", "广州仓", "2026-06-27 09:00:00"),
            ("SKU-SKIRT-KHA-M", "卡其半身裙 M码", 160, 90, "佛山裙装工厂", "佛山仓", "2026-06-27 09:00:00"),
            ("SKU-HOODIE-GRY-L", "灰色短款卫衣 L码", 35, 70, "东莞卫衣供应商", "佛山仓", "2026-06-27 09:00:00"),
            ("SKU-DRESS-FLORAL-S", "碎花连衣裙 S码", 96, 60, "番禺连衣裙工厂", "广州仓", "2026-06-27 09:00:00"),
        ],
    )

    execute_many(
        conn,
        """
        INSERT OR REPLACE INTO exceptions(exception_no, order_no, exception_type, reason, owner, priority, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            ("EXP-001", "SO-2026-001", "库存不足", "黑色连衣裙 M码低于安全库存，可能影响直播间订单发货。", "采购/仓储", "高", "未关闭", "2026-06-27 10:00:00"),
            ("EXP-002", "SO-2026-002", "交期风险", "白色T恤 L码库存缺口大，今日截单后存在延迟发货风险。", "供应链/客服", "高", "处理中", "2026-06-27 10:05:00"),
            ("EXP-003", "SO-2026-004", "物流延迟", "运单揽收后超过24小时未更新，客户已催单。", "客服/物流", "中", "未关闭", "2026-06-27 10:40:00"),
            ("EXP-004", "SO-2026-005", "售后换码", "客户申请 S 码换 M 码，需要核实可用库存。", "客服/仓储", "中", "待客户确认", "2026-06-27 11:15:00"),
        ],
    )

    lead_rows = [
        ("刘女士", "wechat: liu-demo", "咨询黑色连衣裙批量团购和尺码建议", "高", "网站AI客服", "待跟进", "销售一组", "2026-06-27 10:10:00"),
        ("张先生", "wechat: zhang-demo", "企业微信咨询直播间爆款补货合作", "中", "企业微信咨询", "已记录", "销售二组", "2026-06-27 10:20:00"),
        ("陈女士", "phone: 13800000000", "咨询售后换码规则和发货时效", "中", "抖音小店客服", "待跟进", "客服组", "2026-06-27 10:36:00"),
        ("黄女士", "wechat: huang-demo", "希望采购 200 件夏季连衣裙", "高", "直播间订单", "待跟进", "销售一组", "2026-06-27 11:00:00"),
    ]
    if table_count(conn, "customer_leads") == 0:
        execute_many(
            conn,
            """
            INSERT INTO customer_leads(name, contact, demand, intent_level, source, status, owner, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            lead_rows,
        )
    if table_count(conn, "leads") == 0:
        execute_many(
            conn,
            """
            INSERT INTO leads(name, contact, demand, intent_level, source, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [(name, contact, demand, intent, source, status, created_at) for name, contact, demand, intent, source, status, _owner, created_at in lead_rows],
        )

    if table_count(conn, "todos") == 0:
        execute_many(
            conn,
            """
            INSERT INTO todos(title, owner, priority, status, due_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                ("确认黑色连衣裙补货交期", "采购/仓储", "高", "未完成", "2026-06-27"),
                ("跟进白色T恤延迟发货解释话术", "客服组", "高", "未完成", "2026-06-27"),
                ("复核平台回款差异订单", "财务组", "中", "未完成", "2026-06-28"),
                ("整理客服RAG售后规则库", "运营组", "中", "进行中", "2026-06-30"),
            ],
        )

    execute_many(
        conn,
        """
        INSERT OR REPLACE INTO finance_reconcile(order_no, platform, order_amount, received_amount, difference, reason, status, owner, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            ("SO-2026-001", "抖音小店", 398, 398, 0, "已到账", "已对平", "财务组", "2026-06-27 12:00:00"),
            ("SO-2026-002", "天猫店", 495, 465, 30, "平台优惠券未同步", "待复核", "财务组", "2026-06-27 12:05:00"),
            ("SO-2026-003", "拼多多店", 357, 330, 27, "平台扣点差异", "待复核", "财务组", "2026-06-27 12:10:00"),
            ("SO-2026-004", "抖音小店", 199, 0, 199, "退款处理中", "异常", "财务组", "2026-06-27 12:15:00"),
            ("SO-2026-005", "天猫店", 438, 438, 0, "已到账", "已对平", "财务组", "2026-06-27 12:20:00"),
        ],
    )

    if table_count(conn, "ai_reports") == 0:
        execute_many(
            conn,
            """
            INSERT INTO ai_reports(report_type, content, model_route, created_at)
            VALUES (?, ?, ?, ?)
            """,
            [
                ("daily", "【AI业务日报】订单5单，未关闭异常3条，库存预警3个，高意向线索2条。", "daily_report", "2026-06-27 12:30:00"),
                ("exception", "优先处理 EXP-001 库存不足和 EXP-002 交期风险。", "exception_classification", "2026-06-27 12:35:00"),
                ("finance", "发现3笔回款差异，建议财务复核平台优惠券、扣点和退款状态。", "daily_report", "2026-06-27 12:40:00"),
            ],
        )

    if table_count(conn, "workflow_logs") == 0:
        execute_many(
            conn,
            """
            INSERT INTO workflow_logs(workflow_name, trigger_type, status, executed_at, summary, pushed_to_feishu, next_action)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("女装电商AI业务闭环", "manual_demo", "success", "2026-06-27 12:30:00", "同步订单5条，异常3条，库存预警3条，AI日报已生成", "skipped", "配置飞书Webhook后可推送日报到测试群"),
                ("库存预警检查", "scheduled_mock", "warning", "2026-06-27 09:30:00", "发现黑色连衣裙、白色T恤、灰色卫衣低于安全库存", "skipped", "生成采购补货审批"),
                ("财务对账复核", "manual_demo", "warning", "2026-06-26 18:00:00", "发现平台优惠券、扣点、退款导致回款差异", "skipped", "财务复核差异订单"),
            ],
        )
