from __future__ import annotations

import os
from typing import Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


def send_feishu_text(text: str, webhook_url: Optional[str] = None) -> Dict:
    """Send a plain text message to a Feishu custom bot webhook."""
    url = webhook_url or os.getenv("FEISHU_WEBHOOK_URL")
    if not url:
        return {"ok": False, "skipped": True, "reason": "FEISHU_WEBHOOK_URL is empty"}

    payload = {"msg_type": "text", "content": {"text": text}}
    resp = requests.post(url, json=payload, timeout=10)
    return {"ok": resp.ok, "status_code": resp.status_code, "response": safe_json(resp)}


def send_wechat_work_text(text: str, webhook_url: Optional[str] = None) -> Dict:
    """Send a plain text message to a WeCom / 企业微信 group bot webhook."""
    url = webhook_url or os.getenv("WECHAT_WORK_WEBHOOK_URL")
    if not url:
        return {"ok": False, "skipped": True, "reason": "WECHAT_WORK_WEBHOOK_URL is empty"}

    payload = {"msgtype": "text", "text": {"content": text}}
    resp = requests.post(url, json=payload, timeout=10)
    return {"ok": resp.ok, "status_code": resp.status_code, "response": safe_json(resp)}


def notify_all(text: str) -> Dict:
    return {
        "feishu": send_feishu_text(text),
        "wechat_work": send_wechat_work_text(text),
    }


def safe_json(resp: requests.Response):
    try:
        return resp.json()
    except Exception:
        return resp.text[:500]
