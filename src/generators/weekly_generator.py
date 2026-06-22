"""Generate the weekly AI Intelligence review."""
import logging
from datetime import date
from pathlib import Path
from typing import Optional
from src.analyzers.claude_analyzer import analyze, SYSTEM_ANALYST, MODEL_DEEP
from src.collectors.news_collector import collect_rss_news, collect_hacker_news
from src.collectors.arxiv_collector import collect_papers
from src.utils.date_utils import today_beijing, week_label
from src.utils.storage import save_report
from config.settings import REPORTS_DIR

logger = logging.getLogger(__name__)


def _load_week_dailies(week_dir: Path) -> str:
    """Load existing daily reports from this week for context."""
    if not week_dir.exists():
        return ""
    parts = []
    for f in sorted(week_dir.glob("????-??-??.md")):
        content = f.read_text(encoding="utf-8")[:3000]
        parts.append(f"=== {f.stem} ===\n{content}")
    return "\n\n".join(parts)


def generate_weekly_report(target_date: Optional[date] = None) -> str:
    today = target_date or today_beijing()
    label = week_label(today)
    logger.info(f"Generating weekly report for {label}")

    news = collect_rss_news(max_per_source=15)
    papers = collect_papers(max_per_category=20)

    daily_context = _load_week_dailies(REPORTS_DIR / "daily")

    prompt = f"""今天是 {today.strftime('%Y年%m月%d日')}，本周是 {label}。

请生成本周的 AI Intelligence Weekly 深度周报。

输出格式：

# AI Intelligence Weekly — {label}

> XinyMao AI Intelligence Hub | 周度深度复盘

---

## 本周 AI 行业总结

[200字以上，本周AI行业整体走向]

---

## 本周最重要的5件事

[每件事深度分析，结构同日报的"今日最重要的3件事"]

---

## 各大厂商本周动向

### Anthropic / Claude
### OpenAI / ChatGPT
### Google / DeepMind
### Meta AI
### xAI / Grok
### 其他值得关注的玩家

---

## 本周开源亮点

[GitHub 上本周最值得关注的开源项目]

---

## 本周论文精选

[从本周arXiv中选出最重要的5篇，深度分析]

---

## 趋势分析

### 短期趋势（1个月内）
### 中期趋势（3个月内）
### 长期趋势（6-12个月）

---

## 机会与风险

### 本周发现的机会
### 本周需要警惕的风险

---

## 下周预测

[基于本周动态，预测下周可能发生的重要事件]

---

## 本周推荐资源

[本周最值得阅读/观看/实践的资源，3-5个]

---

## 主编周记

[500字以上的个人深度思考，不少于500字]

---

*Weekly 由 XinyMao AI Intelligence Hub 生成 | {label}*

---

原始数据参考（本周日报摘要）：
{daily_context[:5000] if daily_context else "[本周暂无日报数据，请基于已知信息分析]"}

本周最新新闻（前20条）：
{chr(10).join(f"- [{n.source}] {n.title}" for n in news[:20])}

本周重要论文（前15篇）：
{chr(10).join(f"- [{p.category}] {p.title}" for p in papers[:15])}
"""

    report = analyze(prompt, system=SYSTEM_ANALYST, model=MODEL_DEEP, max_tokens=10000)
    filename = f"{label}.md"
    save_report(report, REPORTS_DIR / "weekly", filename)
    logger.info(f"Weekly report saved: reports/weekly/{filename}")
    return report
