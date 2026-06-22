"""Google / DeepMind tracker."""
import logging
from datetime import datetime
from src.utils.storage import save_report, append_tracker_entry
from src.analyzers.claude_analyzer import analyze, SYSTEM_ANALYST
from config.settings import TRACKERS_DIR, BEIJING_TZ

logger = logging.getLogger(__name__)

TRACKER_DIR = TRACKERS_DIR / "google"

GOOGLE_FEEDS = [
    "https://blog.google/technology/ai/rss/",
    "https://deepmind.google/blog/rss.xml",
]


def fetch_google_news() -> list[dict]:
    import feedparser
    items = []
    for url in GOOGLE_FEEDS:
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:10]:
                items.append({
                    "title": e.get("title", ""),
                    "url": e.get("link", ""),
                    "published": e.get("published", ""),
                    "summary": e.get("summary", "")[:500],
                    "source": url,
                })
        except Exception as ex:
            logger.warning(f"Google feed failed {url}: {ex}")
    return items


def run_google_tracker() -> str:
    logger.info("Running Google tracker...")
    TRACKER_DIR.mkdir(parents=True, exist_ok=True)

    news_items = fetch_google_news()

    entry = {
        "date": datetime.now(BEIJING_TZ).strftime("%Y-%m-%d"),
        "timestamp": datetime.now(BEIJING_TZ).isoformat(),
        "news_count": len(news_items),
        "latest_news": news_items[:3],
    }
    append_tracker_entry(TRACKER_DIR, entry)

    news_lines = [
        f"- [{n['published'][:10] if n['published'] else '?'}] [{n['title']}]({n['url']})"
        for n in news_items[:15]
    ]

    prompt = f"""基于以下 Google / DeepMind 最新数据，生成 Google Tracker 更新报告。

格式：

# Google Tracker Update — {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d')}

## 最新动态

## Gemini 生态动态

## DeepMind 研究动态

## Google AI 产品动态

## 分析师点评

---

最新新闻：
{chr(10).join(news_lines) if news_lines else '暂无'}
"""
    report = analyze(prompt, system=SYSTEM_ANALYST, max_tokens=3000)
    today_str = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")
    save_report(report, TRACKER_DIR, f"{today_str}.md")
    _update_tracker_index()
    return report


def _update_tracker_index() -> None:
    entries = [
        f"- [{f.stem}](trackers/google/{f.name})"
        for f in sorted(TRACKER_DIR.glob("????-??-??.md"), reverse=True)[:30]
    ]
    index = f"""# Google Tracker

> Google / DeepMind / Gemini 长期动态追踪 | XinyMao AI Intelligence Hub

## 最新更新

{chr(10).join(entries) if entries else '暂无记录'}
"""
    (TRACKER_DIR / "README.md").write_text(index, encoding="utf-8")
