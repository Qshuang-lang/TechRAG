"""文本预处理与分块。"""
import re
import uuid

import jieba


def normalize(text: str) -> str:
    """去空白与噪声字符。"""
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def tokenize(text: str) -> list[str]:
    """jieba 分词（FAQ TF-IDF 用）。"""
    return [w for w in jieba.cut(text) if w.strip()]


def build_parent_child_chunks(text: str, source: str, parent_size: int = 1000, child_size: int = 300, overlap: int = 50):
    """把长文档切成父块/子块两级：父块入库 MySQL，子块向量化进 Milvus。

    返回 [{
        "parent_id": int, "parent_content": str,
        "children": [{"child_id": str, "content": str}, ...]
    }]
    """
    text = normalize(text)
    if not text:
        return []

    # 按段落粗分
    paragraphs = [p.strip() for p in re.split(r"\n+", text) if p.strip()]

    # 父块：按字符窗口滚动切分
    parents = []
    current = ""
    for para in paragraphs:
        # 单段落超长（如无换行的整页正文）：按 parent_size 窗口先切碎
        while len(para) > parent_size:
            piece = para[:parent_size]
            parents.append(piece)
            para = para[parent_size:]
        if len(current) + len(para) > parent_size and current:
            parents.append(current)
            current = para
        else:
            current = (current + " " + para).strip()
    if current:
        parents.append(current)

    result = []
    for pid, parent in enumerate(parents, start=1):
        children = []
        # 子块：按窗口+重叠切分
        step = child_size - overlap
        chunks = [parent[i:i + child_size] for i in range(0, max(len(parent), 1), step) if parent[i:i + child_size].strip()]
        if not chunks:
            chunks = [parent]
        for c in chunks:
            children.append({"child_id": str(uuid.uuid4()), "content": c})
        result.append({"parent_id": pid, "parent_content": parent, "children": children})

    return result
