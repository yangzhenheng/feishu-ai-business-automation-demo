import os
import tempfile


def test_rule_based_report_contains_key_sections():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["DATABASE_PATH"] = path

    from app.db import get_connection, init_db
    from app.services.business import build_rule_based_report, command_response, customer_service_answer

    init_db()
    conn = get_connection()
    report = build_rule_based_report(conn)

    assert "今日AI业务日报" in report
    assert "库存预警" in report
    assert "客户线索" in report
    assert "AI处理建议" in report
    assert "SO-2026-002" in command_response(conn, "/异常")

    answer = customer_service_answer("我想做网站AI客服和企业微信通知")
    assert answer["intent_level"] in ["高", "中"]
    conn.close()
    os.remove(path)
