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
            customer TEXT NOT NULL,
            sku TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            due_date TEXT NOT NULL,
            owner TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
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
            warehouse TEXT NOT NULL
        )
        """
    )

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

    conn.commit()
    seed_db(conn)
    conn.close()


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]


def seed_db(conn: sqlite3.Connection) -> None:
    if table_count(conn, "orders") == 0:
        execute_many(
            conn,
            """
            INSERT INTO orders(order_no, customer, sku, quantity, due_date, owner, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("SO-2026-001", "华南服装旗舰店", "SKU-TSHIRT-BLK-M", 500, "2026-06-28", "王敏", "生产中", "2026-06-20"),
                ("SO-2026-002", "广州渠道客户A", "SKU-HOODIE-GRY-L", 120, "2026-06-27", "李强", "异常", "2026-06-21"),
                ("SO-2026-003", "直播电商客户B", "SKU-CAP-WHT-F", 1000, "2026-06-30", "陈静", "待发货", "2026-06-22"),
                ("SO-2026-004", "深圳渠道客户C", "SKU-TSHIRT-WHT-L", 300, "2026-06-26", "赵磊", "异常", "2026-06-22"),
                ("SO-2026-005", "跨境电商客户D", "SKU-PANTS-BLK-XL", 200, "2026-07-01", "王敏", "待确认", "2026-06-23"),
            ],
        )

    if table_count(conn, "inventory") == 0:
        execute_many(
            conn,
            """
            INSERT INTO inventory(sku, product_name, current_stock, safety_stock, supplier, warehouse)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                ("SKU-TSHIRT-BLK-M", "黑色T恤 M码", 820, 300, "供应商A", "广州仓"),
                ("SKU-HOODIE-GRY-L", "灰色卫衣 L码", 40, 120, "供应商B", "佛山仓"),
                ("SKU-CAP-WHT-F", "白色鸭舌帽", 2600, 800, "供应商C", "广州仓"),
                ("SKU-TSHIRT-WHT-L", "白色T恤 L码", 80, 200, "供应商A", "广州仓"),
                ("SKU-PANTS-BLK-XL", "黑色长裤 XL码", 380, 150, "供应商D", "东莞仓"),
            ],
        )

    if table_count(conn, "exceptions") == 0:
        execute_many(
            conn,
            """
            INSERT INTO exceptions(exception_no, order_no, exception_type, reason, owner, priority, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("EXP-001", "SO-2026-002", "库存不足", "灰色卫衣 L码库存低于订单需求，需要供应商补货确认。", "李强", "高", "处理中", "2026-06-24"),
                ("EXP-002", "SO-2026-004", "交期风险", "订单交期临近，但白色T恤 L码库存不足，可能影响发货。", "赵磊", "高", "未关闭", "2026-06-24"),
                ("EXP-003", "SO-2026-005", "信息缺失", "客户尺码配比未确认，订单暂未进入生产排期。", "王敏", "中", "待客户确认", "2026-06-24"),
            ],
        )

    if table_count(conn, "leads") == 0:
        execute_many(
            conn,
            """
            INSERT INTO leads(name, contact, demand, intent_level, source, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("张先生", "wechat: zhang-demo", "咨询网站AI客服和自动报价功能", "高", "网站AI客服", "待跟进", "2026-06-24"),
                ("刘女士", "phone: 13800000000", "需要把客户咨询同步到企业微信", "中", "网站表单", "已记录", "2026-06-24"),
            ],
        )

    if table_count(conn, "todos") == 0:
        execute_many(
            conn,
            """
            INSERT INTO todos(title, owner, priority, status, due_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                ("确认 SO-2026-002 补货交期", "李强", "高", "未完成", "2026-06-26"),
                ("跟进 SO-2026-004 发货风险", "赵磊", "高", "未完成", "2026-06-25"),
                ("整理客户线索并推送销售", "陈静", "中", "未完成", "2026-06-26"),
                ("优化AI客服FAQ知识库", "王敏", "中", "进行中", "2026-06-29"),
            ],
        )
