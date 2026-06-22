"""Generate Research Digest from arXiv papers."""
import logging
from datetime import date
from typing import Optional
from src.analyzers.claude_analyzer import analyze, SYSTEM_ANALYST, MODEL_DEFAULT
from src.collectors.arxiv_collector import Paper, collect_papers
from src.utils.date_utils import today_beijing
from src.utils.storage import save_report
from config.settings import REPORTS_DIR

logger = logging.getLogger(__name__)


def _build_research_prompt(today: date, papers: list[Paper]) -> str:
    paper_lines = []
    for i, p in enumerate(papers):
        paper_lines.append(f"## Paper {i+1}: {p.title}")
        paper_lines.append(f"- Category: {p.category}")
        paper_lines.append(f"- arXiv: {p.url}")
        paper_lines.append(f"- Authors: {', '.join(p.authors[:5])}")
        paper_lines.append(f"- Abstract: {p.abstract[:800]}")
        paper_lines.append("")

    papers_text = "\n".join(paper_lines)

    return f"""今天是 {today.strftime('%Y年%m月%d日')}。

请从以下 arXiv 论文中，选出最值得关注的 8-12 篇，生成 Research Digest。

对每篇选中的论文，严格按以下结构输出：

---

## [论文名称]（中文翻译）

**原标题**: [英文原标题]
**arXiv**: [链接]
**类别**: [cs.AI / cs.CL / cs.LG]
**作者**: [主要作者]

### 核心创新
[这篇论文的核心技术创新是什么，不超过100字]

### 解决的问题
[它解决了什么真实问题或研究gap]

### 适合谁阅读
[NLP研究者 / ML工程师 / AI产品经理 / 所有AI从业者 等]

### 复现难度
⭐⭐⭐（1=非常简单 5=极难）
[简述难点]

### 科研价值
[对学术界的影响，高/中/低，理由]

### 工程价值
[对工程实践的影响，高/中/低，理由]

### 我的评价
[独立判断：这篇论文的真实价值，是炒作还是实质贡献，未来影响]

---

完整输出结构：

# Research Digest — {today.strftime('%Y年%m月%d日')}

> XinyMao AI Intelligence Hub | 每日论文精读

---

## 今日论文概览

[2-3句话总结今日论文整体趋势]

**今日收录**: X 篇 | **重点推荐**: X 篇

---

[每篇论文的详细分析，如上格式]

---

## 今日研究趋势

[200字以上，分析今日论文的整体研究方向、热点话题、值得关注的新兴方向]

---

*Research Digest 由 XinyMao AI Intelligence Hub 生成 | {today.strftime('%Y-%m-%d')}*

以下是今日论文原始数据：

{papers_text}

请选取最有价值的论文深度分析，不要每篇都选，要有筛选和判断。
"""


def generate_research_digest(target_date: Optional[date] = None) -> str:
    """Generate daily research digest from arXiv papers."""
    today = target_date or today_beijing()
    logger.info(f"Generating research digest for {today}")

    papers = collect_papers(max_per_category=15)
    logger.info(f"Collected {len(papers)} papers total")

    prompt = _build_research_prompt(today, papers)
    report = analyze(prompt, system=SYSTEM_ANALYST, max_tokens=8000)

    filename = f"{today.strftime('%Y-%m-%d')}-research.md"
    save_report(report, REPORTS_DIR / "daily", filename)
    logger.info(f"Research digest saved: reports/daily/{filename}")

    return report
