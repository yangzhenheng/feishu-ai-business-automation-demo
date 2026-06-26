from __future__ import annotations

import os
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()


def generate_llm_report(rule_report: str, api_key: Optional[str] = None) -> str:
    """Use an OpenAI-compatible API to polish the rule-based report.

    If no API key is provided, return the rule-based report so the demo can run locally.
    """
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        return rule_report

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    prompt = f"""
你是一名企业AI业务自动化助理。请基于以下结构化业务数据，生成一份简洁、专业、可执行的中文业务日报。
要求：
1. 保留关键数字和风险事项。
2. 给出优先级和下一步动作。
3. 语气像企业内部日报，不要夸张。
4. 输出 Markdown。

原始数据：
{rule_report}
""".strip()

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你负责把业务数据整理成专业日报。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    try:
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except Exception as exc:
        return rule_report + f"\n\n> LLM 接口调用失败，已回退到规则日报。错误：{exc}"
