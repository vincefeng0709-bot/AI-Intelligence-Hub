"""Generate the daily AI Intelligence report."""
import logging
from datetime import date
from typing import Optional
from src.analyzers.claude_analyzer import analyze, SYSTEM_ANALYST, MODEL_DEFAULT
from src.collectors.news_collector import (
    NewsItem, collect_rss_news, collect_hacker_news, collect_github_trending
)
from src.collectors.arxiv_collector import Paper, collect_papers
from src.utils.date_utils import today_beijing
from src.utils.storage import save_report
from config.settings import REPORTS_DIR

logger = logging.getLogger(__name__)

MAX_TOKENS_DAILY = 8000


def _format_news_for_prompt(items: list[NewsItem], label: str, limit: int = 8) -> str:
    if not items:
        return f"[{label}: 暂无数据]"
    lines = [f"### {label}"]
    for i, item in enumerate(items[:limit]):
        lines.append(f"{i+1}. **{item.title}**")
        lines.append(f"   来源: {item.source} | URL: {item.url}")
        if item.summary:
            lines.append(f"   摘要: {item.summary[:300]}")
        lines.append("")
    return "\n".join(lines)


def _format_papers_for_prompt(papers: list[Paper], limit: int = 10) -> str:
    if not papers:
        return "[arXiv 论文: 暂无数据]"
    lines = ["### 最新 arXiv 论文"]
    for i, p in enumerate(papers[:limit]):
        lines.append(f"{i+1}. **{p.title}** [{p.category}]")
        lines.append(f"   arXiv: {p.url}")
        lines.append(f"   作者: {', '.join(p.authors[:3])}")
        lines.append(f"   摘要: {p.abstract[:400]}")
        lines.append("")
    return "\n".join(lines)


def _build_daily_prompt(
    today: date,
    news: list[NewsItem],
    papers: list[Paper],
    github: list[NewsItem],
    hn: list[NewsItem],
) -> str:
    anthropic_news = [n for n in news if n.source == "anthropic"]
    openai_news = [n for n in news if n.source == "openai"]
    google_news = [n for n in news if n.source in ("google_deepmind",)]
    meta_news = [n for n in news if n.source == "meta_ai"]
    ms_news = [n for n in news if n.source == "microsoft_ai"]
    hf_news = [n for n in news if n.source == "huggingface"]
    other_news = [n for n in news if n.source not in (
        "anthropic", "openai", "google_deepmind", "meta_ai", "microsoft_ai", "huggingface"
    )]

    prompt = f"""今天是 {today.strftime('%Y年%m月%d日')}。

请根据以下原始数据，生成一份完整的 AI Intelligence Daily 报告。

要求：
1. 不做新闻搬运，做专业分析
2. 每条重要新闻必须分析：发生了什么 / 为什么重要 / 对开发者影响 / 对科研影响 / 对创业影响 / 我的判断
3. 今日最重要的3件事，每件事必须深度分析
4. 我的总结不少于500字，包含趋势分析、机会分析、风险分析、未来6个月影响
5. 严格使用以下 Markdown 结构输出

---

# AI Intelligence Daily — {today.strftime('%Y年%m月%d日')}

> XinyMao AI Intelligence Hub | 专业 · 深度 · 有温度

---

## 今日最重要的3件事

[分析今天最重要的3条新闻，每条用以下结构：]

### 1. [事件标题]

**发生了什么**：

**为什么重要**：

**对开发者影响**：

**对科研影响**：

**对创业影响**：

**我的判断**：

---

## Claude 生态

[分析 Anthropic / Claude 相关动态，无动态则写"今日暂无重要动态"]

---

## OpenAI 生态

[分析 OpenAI / ChatGPT 相关动态]

---

## Google 生态

[分析 Google DeepMind / Gemini 相关动态]

---

## Meta 生态

[分析 Meta AI 相关动态]

---

## xAI 生态

[分析 xAI / Grok 相关动态，无动态则跳过或简述]

---

## 开源项目动态

[基于 GitHub Trending 和 HuggingFace，分析值得关注的开源项目]

---

## 最新论文

[选取最重要的3-5篇论文，用以下结构分析：]

### 论文名称
**核心创新**：
**解决的问题**：
**适合谁阅读**：
**复现难度**：⭐⭐⭐（1-5星）
**科研价值**：
**工程价值**：
**我的评价**：

---

## 社区热点

[基于 Hacker News 分析社区讨论热点]

---

## AI 投资融资

[如有相关新闻则分析，无则跳过]

---

## 我的总结

[不少于500字的深度总结，包含：今日整体趋势 / 值得关注的机会 / 潜在风险 / 未来6个月影响预判]

---

*报告生成时间：{today.strftime('%Y-%m-%d')} | XinyMao AI Intelligence Hub*

---

以下是今日原始数据：

{_format_news_for_prompt(anthropic_news, "Anthropic 官方动态")}

{_format_news_for_prompt(openai_news, "OpenAI 动态")}

{_format_news_for_prompt(google_news, "Google / DeepMind 动态")}

{_format_news_for_prompt(meta_news, "Meta AI 动态")}

{_format_news_for_prompt(ms_news, "Microsoft AI 动态")}

{_format_news_for_prompt(hf_news, "HuggingFace 动态")}

{_format_news_for_prompt(other_news, "其他来源动态")}

{_format_papers_for_prompt(papers, limit=12)}

{_format_news_for_prompt(github, "GitHub Trending AI 项目", limit=10)}

{_format_news_for_prompt(hn, "Hacker News AI 热帖", limit=15)}

请严格按照上面的 Markdown 模板结构输出完整报告。
"""
    return prompt


def generate_daily_report(target_date: Optional[date] = None) -> str:
    """Collect data and generate daily report. Returns the report content."""
    today = target_date or today_beijing()
    logger.info(f"Generating daily report for {today}")

    logger.info("Collecting RSS news...")
    news = collect_rss_news(max_per_source=8)

    logger.info("Collecting arXiv papers...")
    papers = collect_papers(max_per_category=10)

    logger.info("Collecting GitHub trending...")
    github = collect_github_trending()

    logger.info("Collecting Hacker News...")
    hn = collect_hacker_news(limit=20, min_score=30)

    logger.info("Calling Claude for analysis...")
    prompt = _build_daily_prompt(today, news, papers, github, hn)
    report = analyze(prompt, system=SYSTEM_ANALYST, max_tokens=MAX_TOKENS_DAILY)

    filename = f"{today.strftime('%Y-%m-%d')}.md"
    save_report(report, REPORTS_DIR / "daily", filename)
    logger.info(f"Daily report saved: reports/daily/{filename}")

    return report
