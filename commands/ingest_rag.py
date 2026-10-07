"""导入 RAG 文档（待数据准备后使用）：父块入 MySQL，子块向量化入 Milvus。"""
import os

import typer

from clients.embedding import embedding_client
from clients.milvus import milvus
from db.session import SessionLocal
from db.models import RagChildChunk, RagChunk
from logger import get_logger
from utils.chunking import build_parent_child_chunks

logger = get_logger("commands.ingest_rag")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage", "data")


def run(source: str = "", batch_size: int = 10):
    """source: 文本文件、目录 或 .json（[{content, source}]）。"""
    if not source:
        source = os.path.join(DATA_DIR, "rag_docs")
        os.makedirs(source, exist_ok=True)
        logger.info("未指定 source，使用默认目录 %s（当前为空则跳过）", source)

    try:
        documents = _load_documents(source)
    except Exception as e:
        logger.error("文档加载失败: %s", e)
        raise SystemExit(1)

    if not documents:
        logger.info("没有可导入的文档")
        return

    if not milvus.has_collection():
        logger.warning("Milvus 集合不存在，先创建集合")
        milvus.create_collection()

    db = SessionLocal()
    inserted = 0
    try:
        for doc in documents:
            content = doc.get("content", "")
            doc_source = doc.get("source", "未知")
            chunks = build_parent_child_chunks(content, doc_source)
            for pc in chunks:
                parent = RagChunk(content=pc["parent_content"], source=doc_source)
                db.add(parent)
                db.flush()  # 拿到 parent.id
                # 子块分批向量化入库
                children = pc["children"]
                for i in range(0, len(children), batch_size):
                    batch = children[i:i + batch_size]
                    vectors = embedding_client.embed_batch([c["content"] for c in batch])
                    rows = [
                        {
                            "id": _hash_id(c["child_id"]),
                            "vector": vec,
                            "child_id": _hash_id(c["child_id"]),
                            "parent_id": parent.id,
                            "content": c["content"],
                            "source": doc_source,
                        }
                        for c, vec in zip(batch, vectors)
                    ]
                    milvus.insert(rows)
                    db.add_all([RagChildChunk(parent_id=parent.id, content=c["content"]) for c in batch])
                    inserted += len(batch)
                    logger.info("已入库 %d 子块（父块 #%s）", len(batch), parent.id)
        db.commit()
        logger.info("RAG 导入完成，共 %d 子块", inserted)
    except Exception as e:
        db.rollback()
        logger.error("RAG 导入失败: %s", e)
        raise SystemExit(1)
    finally:
        db.close()


def _load_documents(source: str) -> list[dict]:
    """支持 .txt / .md 单文件或目录；.json 形如 [{content, source}]。"""
    docs = []
    if os.path.isdir(source):
        for root, _dirs, files in os.walk(source):
            for fname in files:
                if fname.lower().endswith((".txt", ".md", ".json")):
                    path = os.path.join(root, fname)
                    docs.extend(_load_file(path, fname))
    elif os.path.isfile(source):
        docs.extend(_load_file(source, os.path.basename(source)))
    return docs


def _load_file(path: str, name: str) -> list[dict]:
    if name.lower().endswith(".json"):
        import json

        with open(path, encoding="utf-8") as fp:
            return json.load(fp)
    with open(path, encoding="utf-8") as fp:
        return [{"content": fp.read(), "source": name}]


def _hash_id(uid: str) -> int:
    """字符串 id 转 64 位 int（Milvus 主键用）。"""
    return abs(hash(uid)) % (2**63)
