"""Collect public evidence for the 2026-09-27 through 2026-10-07 catch-up report."""
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import feedparser
import httpx
from bs4 import BeautifulSoup
from dateutil.parser import parse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "data" / "2026-10-07"
TZ = ZoneInfo("Asia/Shanghai")
START = datetime(2026, 9, 27, tzinfo=TZ)
END = min(datetime.now(TZ), datetime(2026, 10, 8, tzinfo=TZ))
FEEDS = {
    "anthropic": "https://www.anthropic.com/rss.xml",
    "openai": "https://openai.com/news/rss.xml",
    "google_ai": "https://blog.google/technology/ai/rss/",
    "google_deepmind": "https://deepmind.google/blog/rss.xml",
    "meta_ai": "https://ai.meta.com/blog/feed/",
    "microsoft_ai": "https://blogs.microsoft.com/ai/feed/",
    "huggingface": "https://huggingface.co/blog/feed.xml",
    "arxiv_ai": "https://rss.arxiv.org/rss/cs.AI",
    "arxiv_cl": "https://rss.arxiv.org/rss/cs.CL",
    "arxiv_lg": "https://rss.arxiv.org/rss/cs.LG",
}


def get(url, params=None):
    with httpx.Client(timeout=35, follow_redirects=True, headers={"User-Agent": "XinyMaoHub/1.0 public-news-research"}) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        return response


def feed_job(pair):
    name, url = pair
    result = {"source": name, "url": url, "items": []}
    try:
        response = get(url)
        (OUT / f"{name}.xml").write_text(response.text, encoding="utf-8")
        feed = feedparser.parse(response.text)
        result["parsed_count"] = len(feed.entries)
        result["bozo"] = bool(feed.bozo)
        result["undated_count"] = 0
        for entry in feed.entries:
            raw_date = entry.get("published", entry.get("updated", ""))
            try:
                published = parse(raw_date)
                if published.tzinfo is None:
                    result["undated_count"] += 1
                    continue
                published = published.astimezone(TZ)
            except (ValueError, TypeError, OverflowError):
                result["undated_count"] += 1
                continue
            if START <= published < END:
                result["items"].append({"title": entry.get("title", ""), "url": entry.get("link", ""),
                    "published_raw": raw_date, "published_bjt": published.isoformat(),
                    "summary": BeautifulSoup(entry.get("summary", ""), "html.parser").get_text(" ", strip=True),
                    "authors": [a.get("name", "") for a in entry.get("authors", [])]})
        if not feed.entries:
            result["error"] = "No entries parsed; this does not prove no news in the period."
    except Exception as exc:
        result["error"] = str(exc)
    return result


def hn_job():
    result = {"source": "hacker_news", "items": [], "minimum_points": 100}
    try:
        params = {"tags": "story", "numericFilters": f"created_at_i>={int(START.timestamp())},created_at_i<{int(END.timestamp())},points>=100", "hitsPerPage": 100}
        first = get("https://hn.algolia.com/api/v1/search_by_date", params).json()
        pages = [first]
        for page in range(1, first.get("nbPages", 1)):
            pages.append(get("https://hn.algolia.com/api/v1/search_by_date", {**params, "page": page}).json())
        (OUT / "hn_raw.json").write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
        hits = [h for page in pages for h in page["hits"]]
        result["fetched_stories"] = len(hits)
        pattern = re.compile(r"\b(ai|llm|llms|gpt|claude|gemini|anthropic|openai|deepmind|mcp|rag|agent|agents|qwen|mistral|deepseek|jev|reasoning)\b|machine learning|artificial intelligence", re.I)
        for h in hits:
            if pattern.search(h.get("title") or ""):
                result["items"].append({"title": h["title"], "url": h.get("url"), "hn_url": f"https://news.ycombinator.com/item?id={h['objectID']}",
                    "published_bjt": datetime.fromtimestamp(h["created_at_i"], TZ).isoformat(), "points": h.get("points"), "comments": h.get("num_comments")})
        result["items"].sort(key=lambda x: x["points"] or 0, reverse=True)
    except Exception as exc:
        result["error"] = str(exc)
    return result


def arxiv_history():
    result = {"source": "arxiv_history", "items": []}
    try:
        query = "(cat:cs.AI OR cat:cs.CL OR cat:cs.LG) AND submittedDate:[202609261600 TO 202610071600]"
        response = get("https://export.arxiv.org/api/query", {"search_query": query, "start": 0, "max_results": 250, "sortBy": "submittedDate", "sortOrder": "descending"})
        (OUT / "arxiv_history.xml").write_text(response.text, encoding="utf-8")
        feed = feedparser.parse(response.text)
        result["query"] = query
        result["total_results"] = feed.feed.get("opensearch_totalresults")
        result["limit"] = 250
        for e in feed.entries:
            published = parse(e.get("published", ""))
            if START <= published.astimezone(TZ) < END:
                result["items"].append({"title": e.get("title", ""), "url": e.get("id", ""), "published_bjt": published.astimezone(TZ).isoformat(),
                    "abstract": e.get("summary", ""), "authors": [a.get("name", "") for a in e.get("authors", [])], "categories": [t.get("term") for t in e.get("tags", [])]})
    except Exception as exc:
        result["error"] = str(exc)
    return result


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=6) as executor:
        feeds = list(executor.map(feed_job, FEEDS.items()))
        hn_future = executor.submit(hn_job)
        arxiv_future = executor.submit(arxiv_history)
        results = feeds + [hn_future.result(), arxiv_future.result()]
    payload = {"start_bjt": START.isoformat(), "cutoff_bjt": END.isoformat(), "collected_at_bjt": datetime.now(TZ).isoformat(),
        "method": "Date-filtered RSS, paginated HN historical search (>=100 points), arXiv date query (latest 250). Official pages verified separately. Not an exhaustive historical archive.", "sources": results}
    (OUT / "collection.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    for r in results:
        print(r["source"], "in-range", len(r["items"]), "error", r.get("error", "none"))
    print("HN top", [(h["published_bjt"][:10], h["title"], h["points"], h["url"]) for h in results[-2]["items"][:20]])


if __name__ == "__main__":
    main()
