"""Elasticsearch 客户端（全文检索辅助，未启用时降级跳过）。"""
from elasticsearch import Elasticsearch

from logger import get_logger

logger = get_logger("clients.elasticsearch")

_ES_URI = "http://127.0.0.1:9200"


class ESClients:
    def __init__(self):
        self._es = None

    @property
    def es(self):
        if self._es is None:
            self._es = Elasticsearch(_ES_URI)
        return self._es

    def ping(self) -> bool:
        try:
            return bool(self.es.ping())
        except Exception:  # 服务未启动
            return False

    def search(self, index: str, query: str, size: int = 5) -> list[dict]:
        if not self.ping():
            logger.warning("Elasticsearch 未启动，跳过全文检索")
            return []
        resp = self.es.search(
            index=index,
            size=size,
            query={"match": {"content": query}},
        )
        return [hit["_source"] for hit in resp["hits"]["hits"]]


es_client = ESClients()
