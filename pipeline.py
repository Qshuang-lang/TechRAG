"""问答流水线：Greeting → FAQ → RAG → Web → Fallback。"""
from logger import get_logger
from services.fallback import fallback_answer
from services.faq import faq_answer
from services.greeting import greeting_answer, is_greeting
from services.rag import rag_answer
from services.web_search import web_answer

logger = get_logger("pipeline")


def ask(question: str, enable_rag: bool = True, enable_web: bool = True) -> dict:
    """按阶段依次尝试，返回 {answer, stage, detail}。"""
    question = (question or "").strip()
    if not question:
        return {"answer": "请告诉我你想问什么～", "stage": "empty", "detail": ""}

    # 1) Greeting
    if is_greeting(question):
        return {"answer": greeting_answer(question), "stage": "greeting", "detail": "greeting"}

    # 2) FAQ
    answer, detail = faq_answer(question)
    if answer:
        return {"answer": answer, "stage": "faq", "detail": detail}

    # 3) RAG
    if enable_rag:
        answer, detail = rag_answer(question)
        if answer:
            return {"answer": answer, "stage": "rag", "detail": detail}

    # 4) Web
    if enable_web:
        answer, detail = web_answer(question)
        if answer:
            return {"answer": answer, "stage": "web", "detail": detail}

    # 5) Fallback
    return {"answer": fallback_answer(question), "stage": "fallback", "detail": "fallback"}
