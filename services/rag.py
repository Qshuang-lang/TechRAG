"""RAG 阶段：Milvus 向量检索 + LLM 生成。"""
from config import config
from clients.embedding import embedding_client
from clients.llm import llm_client
from clients.milvus import milvus
from logger import get_logger
from prompts import RAG_PROMPT

logger = get_logger("services.rag")


def rag_answer(question: str) -> tuple[str | None, str]:
    """返回 (答案, 命中说明)；无集合/无 embedding/无命中返回 (None, 说明)。"""
    if not embedding_client.ready():
        return None, "rag(未配置 EMBEDDING_API_KEY，跳过)"
    if not milvus.has_collection():
        return None, "rag(集合不存在，跳过)"

    try:
        vector = embedding_client.embed(question)
    except Exception as e:
        logger.warning("向量化失败: %s", e)
        return None, f"rag(向量化失败：{e})"

    hits = milvus.search(vector, limit=config.TOP_K, threshold=config.RAG_THRESHOLD)
    if not hits:
        return None, "rag(未命中)"
    if not llm_client.ready():
        return None, "rag(命中但未配置 DEEPSEEK_API_KEY)"

    context = "\n\n".join(
        f"[来源:{h.get('source', '未知')}]\n{h.get('content', '')}" for h in hits
    )
    prompt = RAG_PROMPT.format(context=context, question=question)
    try:
        answer = llm_client.chat(prompt)
        sources = "; ".join({h.get("source", "未知") for h in hits})
        return answer, f"rag(命中 {len(hits)} 条，来源：{sources})"
    except Exception as e:
        logger.warning("RAG 生成失败: %s", e)
        return None, f"rag(生成失败：{e})"
