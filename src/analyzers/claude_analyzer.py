"""Claude API wrapper for AI-powered analysis."""
import logging
from typing import Optional
import anthropic
from config.settings import ANTHROPIC_API_KEY, MODEL_DEFAULT, MODEL_DEEP

logger = logging.getLogger(__name__)


def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def analyze(prompt: str, system: str = "", model: str = MODEL_DEFAULT,
            max_tokens: int = 4096) -> str:
    """Call Claude for analysis and return text response."""
    client = get_client()
    messages = [{"role": "user", "content": prompt}]
    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        kwargs["system"] = system
    try:
        response = client.messages.create(**kwargs)
        return response.content[0].text
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        raise


SYSTEM_ANALYST = """你是 XinyMao AI Intelligence Hub 的首席 AI 分析师。

你的分析风格：
- 不做新闻搬运，做专业分析
- 每条信息都要回答：发生了什么 / 为什么重要 / 对开发者影响 / 对科研影响 / 对创业影响 / 我的判断
- 聚焦趋势分析、机会分析、风险分析
- 语言：中文，专业但易读
- 有独立判断，不跟风，不过度乐观

输出格式严格遵循用户要求的 Markdown 结构。"""
