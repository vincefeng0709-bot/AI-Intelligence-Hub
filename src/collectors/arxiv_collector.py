"""Collect papers from arXiv RSS feeds."""
import feedparser
import logging
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

ARXIV_FEEDS = {
    "cs.AI": "https://rss.arxiv.org/rss/cs.AI",
    "cs.CL": "https://rss.arxiv.org/rss/cs.CL",
    "cs.LG": "https://rss.arxiv.org/rss/cs.LG",
}


@dataclass
class Paper:
    title: str
    abstract: str
    authors: list[str]
    arxiv_id: str
    url: str
    category: str
    published: Optional[str] = None
    tags: list[str] = field(default_factory=list)


def collect_papers(max_per_category: int = 15) -> list[Paper]:
    """Collect latest papers from arXiv cs.AI, cs.CL, cs.LG."""
    papers: list[Paper] = []
    seen_ids: set[str] = set()

    for category, feed_url in ARXIV_FEEDS.items():
        try:
            import httpx
            resp = httpx.get(feed_url, timeout=30, follow_redirects=True)
            feed = feedparser.parse(resp.text)
            count = 0
            for entry in feed.entries:
                if count >= max_per_category:
                    break
                arxiv_id = entry.get("id", "").split("/abs/")[-1].strip()
                if arxiv_id in seen_ids:
                    continue
                seen_ids.add(arxiv_id)

                abstract = entry.get("summary", "").replace("\n", " ").strip()
                authors = []
                if hasattr(entry, "authors"):
                    authors = [a.get("name", "") for a in entry.authors]
                elif "author" in entry:
                    authors = [entry.author]

                papers.append(Paper(
                    title=entry.get("title", "").replace("\n", " ").strip(),
                    abstract=abstract[:2000],
                    authors=authors[:5],
                    arxiv_id=arxiv_id,
                    url=f"https://arxiv.org/abs/{arxiv_id}",
                    category=category,
                    published=entry.get("published", ""),
                ))
                count += 1
            logger.info(f"Collected {count} papers from {category}")
        except Exception as e:
            logger.error(f"Failed to collect from {category}: {e}")

    return papers
