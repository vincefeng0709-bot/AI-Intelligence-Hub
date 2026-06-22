"""Collect AI news from RSS feeds and web sources."""
import feedparser
import logging
from dataclasses import dataclass, field
from typing import Optional
from bs4 import BeautifulSoup
from src.utils.http import fetch

logger = logging.getLogger(__name__)

NEWS_FEEDS = {
    "anthropic": [
        "https://www.anthropic.com/rss.xml",
        "https://www.anthropic.com/news",
    ],
    "openai": [
        "https://openai.com/news/rss.xml",
    ],
    "google_deepmind": [
        "https://deepmind.google/blog/rss.xml",
        "https://blog.google/technology/ai/rss/",
    ],
    "meta_ai": [
        "https://ai.meta.com/blog/feed/",
    ],
    "microsoft_ai": [
        "https://blogs.microsoft.com/ai/feed/",
    ],
    "huggingface": [
        "https://huggingface.co/blog/feed.xml",
    ],
    "the_gradient": [
        "https://thegradient.pub/rss/",
    ],
}

HACKER_NEWS_API = "https://hacker-news.firebaseio.com/v0"


@dataclass
class NewsItem:
    title: str
    url: str
    source: str
    summary: str = ""
    published: str = ""
    tags: list[str] = field(default_factory=list)


def collect_rss_news(max_per_source: int = 10) -> list[NewsItem]:
    """Collect news from all RSS feeds."""
    items: list[NewsItem] = []
    for source, feeds in NEWS_FEEDS.items():
        count = 0
        for feed_url in feeds:
            if count >= max_per_source:
                break
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    if count >= max_per_source:
                        break
                    summary = entry.get("summary", entry.get("description", ""))
                    if summary:
                        soup = BeautifulSoup(summary, "html.parser")
                        summary = soup.get_text(separator=" ").strip()[:1000]
                    items.append(NewsItem(
                        title=entry.get("title", "").strip(),
                        url=entry.get("link", ""),
                        source=source,
                        summary=summary,
                        published=entry.get("published", entry.get("updated", "")),
                    ))
                    count += 1
            except Exception as e:
                logger.warning(f"RSS feed failed {feed_url}: {e}")
        logger.info(f"Collected {count} items from {source}")
    return items


def collect_hacker_news(limit: int = 30, min_score: int = 50) -> list[NewsItem]:
    """Collect AI-related top stories from Hacker News."""
    from src.utils.http import fetch_json
    top_ids = fetch_json(f"{HACKER_NEWS_API}/topstories.json") or []
    ai_keywords = {
        "ai", "llm", "gpt", "claude", "gemini", "machine learning",
        "neural", "openai", "anthropic", "deepmind", "transformer",
        "agent", "rag", "mcp", "model", "inference", "fine-tun",
    }
    items: list[NewsItem] = []
    checked = 0
    for story_id in top_ids[:200]:
        if len(items) >= limit:
            break
        checked += 1
        story = fetch_json(f"{HACKER_NEWS_API}/item/{story_id}.json")
        if not story or story.get("type") != "story":
            continue
        score = story.get("score", 0)
        if score < min_score:
            continue
        title = story.get("title", "").lower()
        if not any(kw in title for kw in ai_keywords):
            continue
        items.append(NewsItem(
            title=story.get("title", ""),
            url=story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
            source="hacker_news",
            summary=f"Score: {score} | Comments: {story.get('descendants', 0)}",
            published=str(story.get("time", "")),
        ))
    logger.info(f"Collected {len(items)} AI stories from HN (checked {checked})")
    return items


def collect_github_trending(language: str = "", since: str = "daily") -> list[NewsItem]:
    """Collect AI-related GitHub trending repos."""
    url = f"https://github.com/trending/{language}?since={since}"
    html = fetch(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    items: list[NewsItem] = []
    ai_keywords = {"llm", "ai", "gpt", "claude", "agent", "rag", "mcp", "nlp",
                   "ml", "deep", "neural", "diffusion", "transformer", "vector"}

    for repo in soup.select("article.Box-row")[:30]:
        name_el = repo.select_one("h2 a")
        if not name_el:
            continue
        repo_path = name_el.get("href", "").strip("/")
        repo_name = repo_path.lower()
        desc_el = repo.select_one("p")
        desc = desc_el.get_text(strip=True) if desc_el else ""

        combined = (repo_name + " " + desc.lower())
        if not any(kw in combined for kw in ai_keywords):
            continue

        stars_el = repo.select_one("a[href$='/stargazers']")
        stars = stars_el.get_text(strip=True) if stars_el else "?"
        today_el = repo.select_one("span.d-inline-block.float-sm-right")
        today_stars = today_el.get_text(strip=True) if today_el else ""

        items.append(NewsItem(
            title=repo_path,
            url=f"https://github.com/{repo_path}",
            source="github_trending",
            summary=f"{desc} | Stars: {stars} | {today_stars}",
        ))

    logger.info(f"Collected {len(items)} AI repos from GitHub Trending")
    return items
