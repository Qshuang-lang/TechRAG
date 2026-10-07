"""Milvus 向量库客户端（懒加载：服务未启动时不影响应用启动）。"""
from pymilvus import MilvusClient, DataType

from config import config
from logger import get_logger

logger = get_logger("clients.milvus")


class MilvusClientWrapper:
    """统一封装 MilvusClient（pymilvus 3.x），连接懒加载。"""

    def __init__(self):
        self.uri = f"http://{config.MILVUS_HOST}:{config.MILVUS_PORT}"
        self.collection = config.MILVUS_COLLECTION
        self.dim = config.MILVUS_DIM
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = MilvusClient(uri=self.uri)
        return self._client

    def _available(self) -> bool:
        """探测 Milvus 是否可用（不可用返回 False 而非抛异常）。"""
        try:
            self._get_client().list_collections()
            return True
        except Exception as e:
            logger.warning("Milvus 不可用（%s）", e)
            return False

    # ---- 集合管理 ----
    def has_collection(self) -> bool:
        if not self._available():
            return False
        try:
            return self._client.has_collection(self.collection)
        except Exception as e:
            logger.warning("查询集合失败: %s", e)
            return False

    def create_collection(self):
        client = self._get_client()
        schema = client.create_schema(
            auto_id=False,
            enable_dynamic_field=False,
            description="TechRAG 企业IT技术知识库向量索引（RAG 检索用，来源为开源官方文档与公开问答）",
        )
        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True, description="主键ID（由子块哈希生成）")
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=self.dim, description="子块文本向量（1024维，余弦相似度检索）")
        schema.add_field(field_name="child_id", datatype=DataType.INT64, description="子块唯一ID（对应MySQL rag_child_chunk）")
        schema.add_field(field_name="parent_id", datatype=DataType.INT64, description="父块ID（对应MySQL rag_chunk，用于回链原文）")
        schema.add_field(field_name="content", datatype=DataType.VARCHAR, max_length=8192, description="子块文本内容（向量检索后供LLM生成回答）")
        schema.add_field(field_name="source", datatype=DataType.VARCHAR, max_length=255, description="文档来源（如 MySQL官方文档 / Stack Overflow）")

        index_params = client.prepare_index_params()
        index_params.add_index(field_name="vector", index_type="AUTOINDEX", metric_type="COSINE")

        client.create_collection(
            collection_name=self.collection,
            schema=schema,
            index_params=index_params,
            description="TechRAG 企业IT技术知识库向量索引（RAG 检索用，来源为开源官方文档与公开问答）",
        )
        logger.info("已创建 Milvus 集合 %s (dim=%s)", self.collection, self.dim)

    def drop_collection(self):
        client = self._get_client()
        if client.has_collection(self.collection):
            client.drop_collection(self.collection)
            logger.info("已删除 Milvus 集合 %s", self.collection)

    # ---- 写入 ----
    def insert(self, rows: list[dict]):
        """rows: [{id, vector, child_id, parent_id, content, source}, ...]"""
        if not rows:
            return
        client = self._get_client()
        client.insert(collection_name=self.collection, data=rows)

    # ---- 检索 ----
    def search(self, vector: list[float], limit: int = 5, threshold: float = 0.0) -> list[dict]:
        client = self._get_client()
        res = client.search(
            collection_name=self.collection,
            data=[vector],
            limit=limit,
            output_fields=["child_id", "parent_id", "content", "source"],
        )
        hits = res[0] if res else []
        return [
            {
                "score": float(hit["distance"]),
                "child_id": hit["entity"].get("child_id"),
                "parent_id": hit["entity"].get("parent_id"),
                "content": hit["entity"].get("content", ""),
                "source": hit["entity"].get("source", ""),
            }
            for hit in hits
            if float(hit["distance"]) >= threshold
        ]


milvus = MilvusClientWrapper()
