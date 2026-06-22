"""Central configuration for XinyMao AI Intelligence Hub."""
import os
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT_DIR = Path(__file__).parent.parent
REPORTS_DIR = ROOT_DIR / "reports"
TRACKERS_DIR = ROOT_DIR / "trackers"
PUBLIC_DIR = ROOT_DIR / "public"
TEMPLATES_DIR = ROOT_DIR / "templates"

BEIJING_TZ = ZoneInfo("Asia/Shanghai")

# Anthropic
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL_DEFAULT = "claude-sonnet-4-6"
MODEL_DEEP = "claude-opus-4-8"

# Data sources
SOURCES = {
    "anthropic": [
        "https://www.anthropic.com/news",
        "https://www.anthropic.com/research",
    ],
    "openai": [
        "https://openai.com/news/",
    ],
    "google": [
        "https://blog.google/technology/ai/",
        "https://deepmind.google/discover/blog/",
    ],
    "meta": [
        "https://ai.meta.com/blog/",
    ],
    "xai": [
        "https://x.ai/blog",
    ],
    "microsoft": [
        "https://blogs.microsoft.com/ai/",
    ],
    "hacker_news": "https://hacker-news.firebaseio.com/v0",
    "arxiv": {
        "cs.AI": "https://rss.arxiv.org/rss/cs.AI",
        "cs.CL": "https://rss.arxiv.org/rss/cs.CL",
        "cs.LG": "https://rss.arxiv.org/rss/cs.LG",
    },
    "github_trending": "https://github.com/trending",
    "papers_with_code": "https://paperswithcode.com/latest",
}

REDDIT_SUBS = ["artificial", "MachineLearning", "LocalLLaMA"]

# Brand
BRAND_NAME = "XinyMao"
SITE_TITLE = "XinyMao AI Intelligence Hub"
SITE_DESCRIPTION = "Daily AI Intelligence for Developers, Researchers and Builders."
SITE_URL = os.environ.get("SITE_URL", "https://vincefeng0709-bot.github.io/AI-Intelligence-Hub")
BASE_PATH = os.environ.get("BASE_PATH", "/AI-Intelligence-Hub")

# GitHub
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY", "")
GITHUB_PAGES_URL = os.environ.get("GITHUB_PAGES_URL", SITE_URL)
