"""Generate the monthly AI Intelligence trends report."""
import logging
from datetime import date
from typing import Optional
from src.analyzers.claude_analyzer import analyze, SYSTEM_ANALYST, MODEL_DEEP
from src.collectors.news_collector import collect_rss_news
from src.collectors.arxiv_collector import collect_papers
from src.utils.date_utils import today_beijing, month_label
from src.utils.storage import save_report, load_json
from config.settings import REPORTS_DIR, TRACKERS_DIR

logger = logging.getLogger(__name__)


def _load_month_weeklies(month: str) -> str:
    """Load weekly reports from this month for context."""
    week_dir = REPORTS_DIR / "weekly"
    if not week_dir.exists():
        return ""
    parts = []
    for f in sorted(week_dir.glob(f"{month[:4]}-W*.md")):
        content = f.read_text(encoding="utf-8")[:4000]
        parts.append(f"=== {f.stem} ===\n{content}")
    return "\n\n".join(parts)


def generate_monthly_report(target_date: Optional[date] = None) -> str:
    today = target_date or today_beijing()
    label = month_label(today)
    logger.info(f"Generating monthly report for {label}")

    news = collect_rss_news(max_per_source=20)
    papers = collect_papers(max_per_category=20)
    weekly_context = _load_month_weeklies(label)

    prompt = f"""今天是 {today.strftime('%Y年%m月%d日')}，本月是 {label}。

请生成本月的 AI Intelligence Monthly 深度月报。

输出格式：

# AI Intelligence Monthly — {label}

> XinyMao AI Intelligence Hub | 月度深度趋势报告

---

## 执行摘要

[300字，本月AI行业一页纸总结，高管级别的概要]

---

## 本月 AI 行业全景

[500字以上，全面回顾本月AI行业发展]

---

## 本月10大事件排行

[按重要性排序，每个事件深度分析，结构同日报]

---

## 各大厂商本月深度分析

### Anthropic / Claude 生态
### OpenAI / ChatGPT 生态
### Google AI 生态
### Meta AI 生态
### 开源生态
### 新兴玩家

---

## 本月技术突破

[本月最重要的技术进展，包含论文和工程实践]

---

## 本月商业动向

[融资、并购、商业化进展]

---

## 趋势深度分析

### 技术趋势
### 商业趋势
### 开源趋势
### 监管趋势

---

## 机会地图

[本月发现的值得关注的创业/研究机会，分类整理]

---

## 风险预警

[本月需要警惕的风险信号]

---

## 未来6个月预测

[基于本月数据，对未来6个月的深度预判]

---

## 本月必读清单

[本月最重要的5篇论文 + 5篇文章 + 5个开源项目]

---

## 主编月记

[800字以上的个人深度思考和展望]

---

*Monthly Trends 由 XinyMao AI Intelligence Hub 生成 | {label}*

---

原始参考数据（本月周报摘要）：
{weekly_context[:6000] if weekly_context else "[本月暂无周报数据，请基于已知信息分析]"}

本月最新新闻：
{chr(10).join(f"- [{n.source}] {n.title}" for n in news[:25])}

本月重要论文：
{chr(10).join(f"- [{p.category}] {p.title}" for p in papers[:20])}
"""

    report = analyze(prompt, system=SYSTEM_ANALYST, model=MODEL_DEEP, max_tokens=12000)
    filename = f"{label}.md"
    save_report(report, REPORTS_DIR / "monthly", filename)
    logger.info(f"Monthly report saved: reports/monthly/{filename}")
    return report
