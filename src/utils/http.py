"""HTTP utilities with retry logic and rate limiting."""
import time
import random
import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; XinyMaoBot/1.0; "
        "+https://github.com/xinymao/ai-intelligence-hub)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8",
}


def fetch(url: str, timeout: int = 30, retries: int = 3) -> Optional[str]:
    """Fetch URL content with retry logic."""
    for attempt in range(retries):
        try:
            with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=timeout) as client:
                resp = client.get(url)
                resp.raise_for_status()
                return resp.text
        except Exception as e:
            logger.warning(f"Attempt {attempt+1}/{retries} failed for {url}: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt + random.uniform(0, 1))
    logger.error(f"All retries failed for {url}")
    return None


def fetch_json(url: str, timeout: int = 30) -> Optional[dict]:
    """Fetch JSON from URL."""
    try:
        with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=timeout) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"JSON fetch failed for {url}: {e}")
        return None
