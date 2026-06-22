"""Generate static HTML site for GitHub Pages."""
import logging
import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import markdown
from config.settings import (
    PUBLIC_DIR, REPORTS_DIR, TRACKERS_DIR, TEMPLATES_DIR,
    SITE_TITLE, SITE_DESCRIPTION, SITE_URL, BRAND_NAME, BEIJING_TZ
)

logger = logging.getLogger(__name__)


def _md_to_html(md_content: str) -> str:
    return markdown.markdown(
        md_content,
        extensions=["tables", "fenced_code", "toc", "nl2br", "sane_lists"],
    )


def _load_template(name: str) -> str:
    path = TEMPLATES_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


BASE_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<title>{title} | {site_title}</title>
<link rel="alternate" type="application/rss+xml" title="{site_title} RSS" href="/feed.xml">
<style>
:root {{
  --bg: #0a0a0a;
  --bg2: #111111;
  --bg3: #1a1a1a;
  --border: #2a2a2a;
  --text: #e8e8e8;
  --text2: #888;
  --accent: #6366f1;
  --accent2: #818cf8;
  --green: #34d399;
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
  --mono: "SF Mono", "Fira Code", "Cascadia Code", monospace;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ font-size: 16px; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: var(--font);
  line-height: 1.7;
  min-height: 100vh;
}}
a {{ color: var(--accent2); text-decoration: none; }}
a:hover {{ text-decoration: underline; color: var(--accent); }}

/* Nav */
nav {{
  border-bottom: 1px solid var(--border);
  padding: 0 2rem;
  position: sticky; top: 0; z-index: 100;
  background: rgba(10,10,10,0.95);
  backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: space-between;
  height: 60px;
}}
.nav-brand {{
  font-size: 0.95rem; font-weight: 600; color: var(--text);
  letter-spacing: -0.02em;
}}
.nav-brand span {{ color: var(--accent2); }}
.nav-links {{ display: flex; gap: 2rem; }}
.nav-links a {{
  color: var(--text2); font-size: 0.875rem;
  transition: color 0.2s;
}}
.nav-links a:hover {{ color: var(--text); text-decoration: none; }}

/* Main layout */
.container {{
  max-width: 900px; margin: 0 auto; padding: 3rem 2rem;
}}
.hero {{
  text-align: center; padding: 5rem 2rem 3rem;
  border-bottom: 1px solid var(--border);
}}
.hero h1 {{
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 700; letter-spacing: -0.04em;
  line-height: 1.1; margin-bottom: 1rem;
  background: linear-gradient(135deg, var(--text) 0%, var(--text2) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
.hero p {{
  color: var(--text2); font-size: 1.125rem; max-width: 600px; margin: 0 auto 2rem;
}}
.badge {{
  display: inline-block; padding: 0.25rem 0.75rem;
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: 999px; font-size: 0.75rem; color: var(--text2);
  font-family: var(--mono);
}}

/* Cards */
.card-grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem; margin: 2rem 0;
}}
.card {{
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 12px; padding: 1.5rem;
  transition: border-color 0.2s, transform 0.2s;
}}
.card:hover {{
  border-color: var(--accent); transform: translateY(-2px);
}}
.card-label {{
  font-size: 0.7rem; font-family: var(--mono); color: var(--accent2);
  text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem;
}}
.card h3 {{ font-size: 1rem; margin-bottom: 0.5rem; color: var(--text); }}
.card p {{ font-size: 0.875rem; color: var(--text2); line-height: 1.5; }}
.card-date {{ font-size: 0.75rem; color: var(--text2); margin-top: 1rem; font-family: var(--mono); }}

/* Article content */
.article-header {{ margin-bottom: 3rem; padding-bottom: 2rem; border-bottom: 1px solid var(--border); }}
.article-header h1 {{ font-size: clamp(1.5rem, 4vw, 2.5rem); font-weight: 700; letter-spacing: -0.03em; }}
.article-meta {{ color: var(--text2); font-size: 0.875rem; margin-top: 1rem; font-family: var(--mono); }}
.article-content h2 {{
  font-size: 1.5rem; margin: 2.5rem 0 1rem; color: var(--text);
  border-bottom: 1px solid var(--border); padding-bottom: 0.5rem;
}}
.article-content h3 {{ font-size: 1.125rem; margin: 2rem 0 0.75rem; color: var(--accent2); }}
.article-content p {{ margin-bottom: 1.25rem; }}
.article-content ul, .article-content ol {{ margin: 1rem 0 1rem 1.5rem; }}
.article-content li {{ margin-bottom: 0.5rem; }}
.article-content blockquote {{
  border-left: 3px solid var(--accent); padding-left: 1.5rem;
  color: var(--text2); margin: 1.5rem 0; font-style: italic;
}}
.article-content code {{
  background: var(--bg3); padding: 0.2em 0.4em; border-radius: 4px;
  font-family: var(--mono); font-size: 0.875em; color: var(--accent2);
}}
.article-content pre {{
  background: var(--bg3); padding: 1.5rem; border-radius: 8px;
  overflow-x: auto; margin: 1.5rem 0; border: 1px solid var(--border);
}}
.article-content pre code {{ background: none; padding: 0; color: var(--text); }}
.article-content hr {{
  border: none; border-top: 1px solid var(--border); margin: 2rem 0;
}}
.article-content strong {{ color: var(--text); }}
.article-content table {{
  width: 100%; border-collapse: collapse; margin: 1.5rem 0;
}}
.article-content th {{
  background: var(--bg3); padding: 0.75rem 1rem; text-align: left;
  border: 1px solid var(--border); font-size: 0.875rem;
}}
.article-content td {{
  padding: 0.75rem 1rem; border: 1px solid var(--border); font-size: 0.875rem;
}}

/* List page */
.report-list {{ margin: 2rem 0; }}
.report-item {{
  display: flex; align-items: baseline; gap: 1rem;
  padding: 1rem 0; border-bottom: 1px solid var(--border);
}}
.report-item:last-child {{ border-bottom: none; }}
.report-item-date {{
  font-size: 0.8rem; color: var(--text2); font-family: var(--mono);
  min-width: 100px; flex-shrink: 0;
}}
.report-item-title {{ font-size: 0.95rem; }}

/* Footer */
footer {{
  border-top: 1px solid var(--border); padding: 2rem;
  text-align: center; color: var(--text2); font-size: 0.8rem;
}}

/* Responsive */
@media (max-width: 768px) {{
  nav {{ padding: 0 1rem; }}
  .nav-links {{ gap: 1rem; }}
  .container {{ padding: 2rem 1rem; }}
  .hero {{ padding: 3rem 1rem 2rem; }}
}}

/* Status indicator */
.status-ok {{ color: var(--green); }}
.status-warn {{ color: #f59e0b; }}
.tag {{
  display: inline-block; padding: 0.2rem 0.6rem;
  background: var(--bg3); border: 1px solid var(--border);
  border-radius: 4px; font-size: 0.7rem; font-family: var(--mono);
  color: var(--text2); margin-right: 0.3rem;
}}
</style>
</head>
<body>
<nav>
  <div class="nav-brand">{brand}<span>.</span></div>
  <div class="nav-links">
    <a href="/">Home</a>
    <a href="/daily/">Daily</a>
    <a href="/weekly/">Weekly</a>
    <a href="/monthly/">Monthly</a>
    <a href="/research/">Research</a>
    <a href="/trackers/">Trackers</a>
  </div>
</nav>
{body}
<footer>
  <p>© 2025 {site_title} · Built with Claude · <a href="/feed.xml">RSS</a></p>
  <p style="margin-top: 0.5rem;">Daily AI Intelligence for Developers, Researchers and Builders.</p>
</footer>
</body>
</html>"""


def _render_page(title: str, description: str, body: str, url: str = "") -> str:
    return BASE_HTML.format(
        title=title,
        description=description,
        url=url or SITE_URL,
        site_title=SITE_TITLE,
        brand=BRAND_NAME,
        body=body,
    )


def _generate_index_page(daily_reports: list[Path], weekly_reports: list[Path]) -> str:
    latest_daily = daily_reports[0] if daily_reports else None
    latest_daily_html = ""
    if latest_daily and latest_daily.exists():
        content = latest_daily.read_text(encoding="utf-8")
        preview = content[:800]
        latest_daily_html = f"""
<div class="container" style="padding-top: 2rem; padding-bottom: 0;">
  <div class="card-label">Latest Daily Report</div>
  <h2 style="margin-bottom: 1rem; font-size: 1.25rem;">{latest_daily.stem}</h2>
  <div class="article-content" style="color: var(--text2);">
    {_md_to_html(preview)}...
  </div>
  <p style="margin-top: 1rem;"><a href="/daily/{latest_daily.stem}.html">Read full report →</a></p>
</div>
"""

    recent_daily_cards = ""
    for r in daily_reports[:6]:
        stem = r.stem
        if stem.endswith("-research"):
            continue
        recent_daily_cards += f"""
<a href="/daily/{stem}.html" style="text-decoration:none;">
<div class="card">
  <div class="card-label">Daily Intelligence</div>
  <h3>{stem}</h3>
  <p>AI Intelligence Daily Report</p>
  <div class="card-date">{stem}</div>
</div>
</a>"""

    body = f"""
<div class="hero">
  <div class="badge">LIVE · Daily AI Intelligence</div>
  <h1>XinyMao AI<br>Intelligence Hub</h1>
  <p>{SITE_DESCRIPTION}</p>
</div>
{latest_daily_html}
<div class="container">
  <h2 style="margin-bottom: 1.5rem; font-size: 1.25rem;">Recent Reports</h2>
  <div class="card-grid">
    {recent_daily_cards}
  </div>
  <p style="margin-top: 1.5rem; text-align: center;">
    <a href="/daily/">View all daily reports →</a>
  </p>
</div>
"""
    return _render_page(SITE_TITLE, SITE_DESCRIPTION, body)


def _generate_list_page(reports: list[Path], section_title: str, section_path: str) -> str:
    items_html = ""
    for r in reports:
        stem = r.stem
        items_html += f"""
<div class="report-item">
  <span class="report-item-date">{stem[:10]}</span>
  <a href="/{section_path}/{stem}.html" class="report-item-title">{stem}</a>
</div>"""

    body = f"""
<div class="container">
  <div class="article-header">
    <div class="card-label">{section_title}</div>
    <h1>{section_title}</h1>
    <p class="article-meta">Total: {len(reports)} reports</p>
  </div>
  <div class="report-list">
    {items_html}
  </div>
</div>"""
    return _render_page(section_title, SITE_DESCRIPTION, body)


def _generate_article_page(md_path: Path, section_path: str) -> str:
    content = md_path.read_text(encoding="utf-8")
    html_content = _md_to_html(content)
    title = md_path.stem
    url = f"{SITE_URL}/{section_path}/{title}.html"

    body = f"""
<div class="container">
  <article>
    <div class="article-header">
      <div class="card-label">{section_path.upper()}</div>
      <p class="article-meta">{title}</p>
    </div>
    <div class="article-content">
      {html_content}
    </div>
  </article>
</div>"""
    return _render_page(title, SITE_DESCRIPTION, body, url)


def _generate_rss_feed(reports: list[Path], label: str) -> str:
    items = []
    for r in reports[:20]:
        content = r.read_text(encoding="utf-8")[:2000]
        pub_date = r.stem[:10]
        items.append(f"""
  <item>
    <title>{r.stem}</title>
    <link>{SITE_URL}/daily/{r.stem}.html</link>
    <description><![CDATA[{content}]]></description>
    <pubDate>{pub_date}</pubDate>
    <guid>{SITE_URL}/daily/{r.stem}.html</guid>
  </item>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>{SITE_TITLE}</title>
  <link>{SITE_URL}</link>
  <description>{SITE_DESCRIPTION}</description>
  <language>zh-CN</language>
  {''.join(items)}
</channel>
</rss>"""


def _generate_sitemap(all_pages: list[str]) -> str:
    urls = "\n".join(
        f"  <url><loc>{SITE_URL}{p}</loc></url>" for p in all_pages
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{SITE_URL}/</loc></url>
{urls}
</urlset>"""


def build_site() -> None:
    """Build the complete static site into public/."""
    logger.info("Building static site...")
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    # Collect all report paths
    daily_reports = sorted(
        [p for p in (REPORTS_DIR / "daily").glob("????-??-??.md")],
        reverse=True
    )
    research_reports = sorted(
        [p for p in (REPORTS_DIR / "daily").glob("*-research.md")],
        reverse=True
    )
    weekly_reports = sorted((REPORTS_DIR / "weekly").glob("*.md"), reverse=True)
    monthly_reports = sorted((REPORTS_DIR / "monthly").glob("*.md"), reverse=True)

    all_page_urls = []

    # Index
    (PUBLIC_DIR / "index.html").write_text(
        _generate_index_page(daily_reports, weekly_reports), encoding="utf-8"
    )

    # Daily section
    daily_dir = PUBLIC_DIR / "daily"
    daily_dir.mkdir(exist_ok=True)
    (daily_dir / "index.html").write_text(
        _generate_list_page(daily_reports, "AI Intelligence Daily", "daily"),
        encoding="utf-8"
    )
    for r in daily_reports:
        out = daily_dir / f"{r.stem}.html"
        out.write_text(_generate_article_page(r, "daily"), encoding="utf-8")
        all_page_urls.append(f"/daily/{r.stem}.html")

    # Research section
    research_dir = PUBLIC_DIR / "research"
    research_dir.mkdir(exist_ok=True)
    (research_dir / "index.html").write_text(
        _generate_list_page(research_reports, "Research Digest", "research"),
        encoding="utf-8"
    )
    for r in research_reports:
        out = research_dir / f"{r.stem}.html"
        out.write_text(_generate_article_page(r, "research"), encoding="utf-8")
        all_page_urls.append(f"/research/{r.stem}.html")

    # Weekly section
    weekly_dir = PUBLIC_DIR / "weekly"
    weekly_dir.mkdir(exist_ok=True)
    (weekly_dir / "index.html").write_text(
        _generate_list_page(weekly_reports, "AI Intelligence Weekly", "weekly"),
        encoding="utf-8"
    )
    for r in weekly_reports:
        out = weekly_dir / f"{r.stem}.html"
        out.write_text(_generate_article_page(r, "weekly"), encoding="utf-8")
        all_page_urls.append(f"/weekly/{r.stem}.html")

    # Monthly section
    monthly_dir = PUBLIC_DIR / "monthly"
    monthly_dir.mkdir(exist_ok=True)
    (monthly_dir / "index.html").write_text(
        _generate_list_page(monthly_reports, "AI Intelligence Monthly", "monthly"),
        encoding="utf-8"
    )
    for r in monthly_reports:
        out = monthly_dir / f"{r.stem}.html"
        out.write_text(_generate_article_page(r, "monthly"), encoding="utf-8")
        all_page_urls.append(f"/monthly/{r.stem}.html")

    # Trackers section
    trackers_dir = PUBLIC_DIR / "trackers"
    trackers_dir.mkdir(exist_ok=True)
    _build_trackers_pages(trackers_dir, all_page_urls)

    # RSS
    (PUBLIC_DIR / "feed.xml").write_text(
        _generate_rss_feed(daily_reports, "Daily"), encoding="utf-8"
    )

    # Sitemap
    (PUBLIC_DIR / "sitemap.xml").write_text(
        _generate_sitemap(all_page_urls), encoding="utf-8"
    )

    # robots.txt
    (PUBLIC_DIR / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8"
    )

    logger.info(f"Site built: {len(all_page_urls)} pages in {PUBLIC_DIR}")


def _build_trackers_pages(trackers_pub_dir: Path, all_page_urls: list) -> None:
    tracker_names = ["claude", "openai", "google"]
    tracker_cards = ""
    for name in tracker_names:
        tracker_dir = TRACKERS_DIR / name
        reports = sorted(tracker_dir.glob("????-??-??.md"), reverse=True) if tracker_dir.exists() else []
        pub_dir = trackers_pub_dir / name
        pub_dir.mkdir(exist_ok=True)

        list_html = _generate_list_page(reports, f"{name.title()} Tracker", f"trackers/{name}")
        (pub_dir / "index.html").write_text(list_html, encoding="utf-8")

        for r in reports:
            out = pub_dir / f"{r.stem}.html"
            out.write_text(_generate_article_page(r, f"trackers/{name}"), encoding="utf-8")
            all_page_urls.append(f"/trackers/{name}/{r.stem}.html")

        latest = reports[0].stem if reports else "No data yet"
        tracker_cards += f"""
<a href="/trackers/{name}/" style="text-decoration:none;">
<div class="card">
  <div class="card-label">Tracker</div>
  <h3>{name.title()} Tracker</h3>
  <p>Latest: {latest}</p>
</div>
</a>"""

    body = f"""
<div class="container">
  <div class="article-header">
    <div class="card-label">Trackers</div>
    <h1>AI Company Trackers</h1>
    <p class="article-meta">Long-term monitoring of major AI labs</p>
  </div>
  <div class="card-grid">
    {tracker_cards}
  </div>
</div>"""
    (trackers_pub_dir / "index.html").write_text(
        _render_page("Trackers", SITE_DESCRIPTION, body), encoding="utf-8"
    )
