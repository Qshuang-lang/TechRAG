"""Fallback 阶段：兜底话术。"""
from clients.llm import llm_client
from logger import get_logger
from prompts import FALLBACK_PROMPT

logger = get_logger("services.fallback")


def fallback_answer(question: str) -> str:
    if not llm_client.ready():
        return "这个问题暂时不在我的知识库里，稍后我可以接入更多资料后再回答你。"
    try:
        return llm_client.chat(FALLBACK_PROMPT.format(question=question), temperature=0.2, max_tokens=256)
    except Exception as e:
        logger.warning("Fallback 生成失败: %s", e)
        return "抱歉，这个问题暂时不在知识库范围内，建议联系人工技术支持。"
