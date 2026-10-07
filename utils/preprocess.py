"""FAQ 匹配预处理：分词入库。"""
from utils.chunking import tokenize


def faq_tokens(question: str) -> str:
    """返回空格分隔的分词串，存 FAQ.tokens 字段。"""
    return " ".join(tokenize(question))
