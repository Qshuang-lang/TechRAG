"""联网搜索阶段：SerpAPI + LLM 生成。"""
from config import config
from clients.llm import llm_client
from logger import get_logger
from prompts import WEB_PROMPT

logger = get_logger("services.web_search")


def web_answer(question: str) -> tuple[str | None, str]:
    """返回 (答案, 命中说明)；无 Key 或无结果返回 (None, 说明)。"""
    if not config.SERPAPI_KEY:
        return None, "web(未配置 SERPAPI_KEY，跳过)"

    try:
        from serpapi import GoogleSearch

        params = {"q": question, "api_key": config.SERPAPI_KEY, "num": 5}
        results = GoogleSearch(params).get_dict().get("organic_results", [])
    except Exception as e:
        logger.warning("SerpAPI 调用失败: %s", e)
        return None, f"web(搜索失败：{e})"

    if not results:
        return None, "web(无搜索结果)"

    context = "\n\n".join(f"[来源:{r.get('link', '未知')}]\n{r.get('snippet', '')}" for r in results)
    prompt = WEB_PROMPT.format(context=context, question=question)
    try:
        answer = llm_client.chat(prompt)
        sources = "; ".join({r.get("link", "") for r in results if r.get("link")})
        return answer, f"web(搜索 {len(results)} 条，来源：{sources})"
    except Exception as e:
        logger.warning("WEB 生成失败: %s", e)
        return None, f"web(生成失败：{e})"
