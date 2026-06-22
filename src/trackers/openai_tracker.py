"""OpenAI tracker — monitors news, API updates, ChatGPT changes."""
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from src.utils.http import fetch_json
from src.utils.storage import save_report, append_tracker_entry, save_json
from src.analyzers.claude_analyzer import analyze, SYSTEM_ANALYST
from config.settings import TRACKERS_DIR, BEIJING_TZ

logger = logging.getLogger(__name__)

TRACKER_DIR = TRACKERS_DIR / "openai"

OPENAI_STATUS_API = "https://status.openai.com/api/v2/status.json"
OPENAI_INCIDENTS_API = "https://status.openai.com/api/v2/incidents.json"


def fetch_openai_status() -> dict:
    status = fetch_json(OPENAI_STATUS_API) or {}
    incidents = fetch_json(OPENAI_INCIDENTS_API) or {}
    return {
        "status": status,
        "recent_incidents": incidents.get("incidents", [])[:10],
        "fetched_at": datetime.now(BEIJING_TZ).isoformat(),
    }


def fetch_openai_news() -> list[dict]:
    import feedparser
    feed = feedparser.parse("https://openai.com/news/rss.xml")
    return [
        {
            "title": e.get("title", ""),
            "url": e.get("link", ""),
            "published": e.get("published", ""),
            "summary": e.get("summary", "")[:500],
        }
        for e in feed.entries[:15]
    ]


def run_openai_tracker() -> str:
    logger.info("Running OpenAI tracker...")
    TRACKER_DIR.mkdir(parents=True, exist_ok=True)

    status_data = fetch_openai_status()
    news_items = fetch_openai_news()

    save_json(status_data, TRACKER_DIR / "latest_status.json")

    entry = {
        "date": datetime.now(BEIJING_TZ).strftime("%Y-%m-%d"),
        "timestamp": datetime.now(BEIJING_TZ).isoformat(),
        "status_indicator": status_data.get("status", {}).get("status", {}).get("indicator", "unknown"),
        "incident_count": len(status_data.get("recent_incidents", [])),
        "latest_news": news_items[:3],
    }
    append_tracker_entry(TRACKER_DIR, entry)

    incident_lines = [
        f"- **{i.get('name','')}** ({i.get('status','')})"
        for i in status_data.get("recent_incidents", [])[:5]
    ]
    news_lines = [
        f"- [{n['published'][:10] if n['published'] else '?'}] [{n['title']}]({n['url']})"
        for n in news_items[:10]
    ]

    raw_context = f"""
OpenAI 系统状态：
- Indicator: {status_data.get('status', {}).get('status', {}).get('indicator', 'N/A')}

近期事故：
{chr(10).join(incident_lines) if incident_lines else '暂无'}

最新新闻：
{chr(10).join(news_lines) if news_lines else '暂无'}
"""

    prompt = f"""基于以下 OpenAI 最新数据，生成 OpenAI Tracker 更新报告。

格式：

# OpenAI Tracker Update — {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d')}

## 系统状态

## 近期事故记录

## 最新动态

## 模型与产品动态

## 分析师点评

---

原始数据：
{raw_context}
"""
    report = analyze(prompt, system=SYSTEM_ANALYST, max_tokens=3000)
    today_str = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
    save_report(report, TRACKER_DIR, f"{today_str}.md")
    _update_tracker_index()
    return report


def _update_tracker_index() -> None:
    entries = [
        f"- [{f.stem}](trackers/openai/{f.name})"
        for f in sorted(TRACKER_DIR.glob("????-??-??.md"), reverse=True)[:30]
    ]
    index = f"""# OpenAI Tracker

> OpenAI / ChatGPT 长期动态追踪 | XinyMao AI Intelligence Hub

## 最新更新

{chr(10).join(entries) if entries else '暂无记录'}
"""
    (TRACKER_DIR / "README.md").write_text(index, encoding="utf-8")
