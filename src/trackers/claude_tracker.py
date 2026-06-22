"""Claude / Anthropic tracker — monitors model releases, API updates, status events."""
import logging
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from src.utils.http import fetch, fetch_json
from src.utils.storage import save_report, append_tracker_entry, save_json, load_json
from src.analyzers.claude_analyzer import analyze, SYSTEM_ANALYST
from config.settings import TRACKERS_DIR, BEIJING_TZ

logger = logging.getLogger(__name__)

TRACKER_DIR = TRACKERS_DIR / "claude"

CLAUDE_STATUS_API = "https://status.anthropic.com/api/v2/status.json"
CLAUDE_INCIDENTS_API = "https://status.anthropic.com/api/v2/incidents.json"
ANTHROPIC_NEWS_RSS = "https://www.anthropic.com/rss.xml"


def fetch_anthropic_status() -> dict:
    """Fetch Claude/Anthropic status page data."""
    status = fetch_json(CLAUDE_STATUS_API) or {}
    incidents_data = fetch_json(CLAUDE_INCIDENTS_API) or {}
    return {
        "status": status,
        "recent_incidents": incidents_data.get("incidents", [])[:10],
        "fetched_at": datetime.now(BEIJING_TZ).isoformat(),
    }


def fetch_anthropic_news() -> list[dict]:
    """Fetch latest Anthropic news via RSS."""
    import feedparser
    feed = feedparser.parse(ANTHROPIC_NEWS_RSS)
    items = []
    for entry in feed.entries[:20]:
        items.append({
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "published": entry.get("published", ""),
            "summary": entry.get("summary", "")[:500],
        })
    return items


def run_claude_tracker() -> str:
    """Run Claude tracker, save data, generate tracker report."""
    logger.info("Running Claude tracker...")
    TRACKER_DIR.mkdir(parents=True, exist_ok=True)

    # Fetch data
    status_data = fetch_anthropic_status()
    news_items = fetch_anthropic_news()

    # Persist raw data
    save_json(status_data, TRACKER_DIR / "latest_status.json")

    # Append to history
    entry = {
        "date": datetime.now(BEIJING_TZ).strftime("%Y-%m-%d"),
        "timestamp": datetime.now(BEIJING_TZ).isoformat(),
        "status_indicator": status_data.get("status", {}).get("status", {}).get("indicator", "unknown"),
        "status_description": status_data.get("status", {}).get("status", {}).get("description", ""),
        "incident_count": len(status_data.get("recent_incidents", [])),
        "latest_news": news_items[:3],
    }
    append_tracker_entry(TRACKER_DIR, entry)

    # Build tracker report
    incident_lines = []
    for inc in status_data.get("recent_incidents", [])[:5]:
        incident_lines.append(f"- **{inc.get('name', '')}** ({inc.get('status', '')}): {inc.get('shortlink', '')}")

    news_lines = [f"- [{n['published'][:10] if n['published'] else '?'}] [{n['title']}]({n['url']})"
                  for n in news_items[:10]]

    raw_context = f"""
Anthropic 系统状态：
- Indicator: {status_data.get('status', {}).get('status', {}).get('indicator', 'N/A')}
- Description: {status_data.get('status', {}).get('status', {}).get('description', 'N/A')}

近期事故：
{chr(10).join(incident_lines) if incident_lines else '暂无近期事故'}

最新新闻：
{chr(10).join(news_lines) if news_lines else '暂无新闻'}
"""

    prompt = f"""请基于以下 Anthropic / Claude 最新数据，生成一份 Claude Tracker 更新报告。

格式：

# Claude Tracker Update — {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d')}

## 系统状态

[当前 Claude API 和服务状态]

## 近期事故记录

[最近的故障和事件记录]

## 最新动态

[Anthropic 最新新闻和公告分析]

## 模型动态

[关于 Claude 模型版本、能力、API 的最新信息]

## 分析师点评

[对 Anthropic 近期动向的专业判断，100-200字]

---

原始数据：
{raw_context}
"""

    report = analyze(prompt, system=SYSTEM_ANALYST, max_tokens=3000)

    today_str = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
    save_report(report, TRACKER_DIR, f"{today_str}.md")

    # Update index
    _update_tracker_index()

    logger.info(f"Claude tracker update saved: trackers/claude/{today_str}.md")
    return report


def _update_tracker_index() -> None:
    """Regenerate the tracker index markdown."""
    entries = []
    for f in sorted(TRACKER_DIR.glob("????-??-??.md"), reverse=True)[:30]:
        entries.append(f"- [{f.stem}](trackers/claude/{f.name})")

    index = f"""# Claude Tracker

> Anthropic / Claude 长期动态追踪 | XinyMao AI Intelligence Hub

## 最新更新

{chr(10).join(entries) if entries else '暂无记录'}

## 关注内容

- Claude 模型发布与更新
- API 功能变更
- Claude Code 更新
- Anthropic 重要公告
- 系统状态与故障历史
"""
    (TRACKER_DIR / "README.md").write_text(index, encoding="utf-8")
