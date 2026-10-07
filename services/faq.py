"""FAQ 阶段：基于 TF-IDF 的短问短答匹配。

先尝试精确/包含匹配；未命中时用 TF-IDF 向量余弦相似度，超过阈值即返回。
FAQ 数据从 MySQL 读取（为空时自动跳过该阶段）。
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import config
from db.session import SessionLocal
from db.models import Faq
from logger import get_logger
from utils.chunking import tokenize

logger = get_logger("services.faq")

_FAQ_CACHE: list[dict] | None = None  # [{question, answer, tokens}]


def _load_faqs() -> list[dict]:
    global _FAQ_CACHE
    if _FAQ_CACHE is None:
        try:
            db = SessionLocal()
            rows = db.query(Faq).all()
            db.close()
            _FAQ_CACHE = [{"question": r.question, "answer": r.answer, "tokens": r.tokens or r.question} for r in rows]
            logger.info("加载 FAQ %d 条", len(_FAQ_CACHE))
        except Exception as e:
            logger.warning("FAQ 加载失败（MySQL 可能未启动）: %s", e)
            _FAQ_CACHE = []
    return _FAQ_CACHE


def faq_answer(question: str) -> tuple[str | None, str]:
    """返回 (答案, 命中说明)；未命中返回 (None, 说明)。"""
    faqs = _load_faqs()
    if not faqs:
        return None, "faq(题库为空，跳过)"

    # 1) 精确/包含匹配
    for f in faqs:
        if question.strip() in f["question"] or f["question"] in question:
            return f["answer"], f"faq(精确命中：{f['question'][:20]})"

    # 2) TF-IDF 余弦相似度
    corpus = [f["tokens"] for f in faqs] + [question]
    try:
        tfidf = TfidfVectorizer(tokenizer=tokenize, token_pattern=None)
        matrix = tfidf.fit_transform(corpus)
        sims = cosine_similarity(matrix[-1:], matrix[:-1])[0]
        best_idx = int(sims.argmax())
        best_score = float(sims[best_idx])
        if best_score >= config.FAQ_THRESHOLD:
            return faqs[best_idx]["answer"], f"faq(TF-IDF 相似度 {best_score:.2f})"
    except Exception as e:
        logger.warning("TF-IDF 匹配异常: %s", e)

    return None, "faq(未命中)"
