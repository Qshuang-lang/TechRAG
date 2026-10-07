"""文本向量化客户端（OpenAI 兼容协议，懒加载；DeepSeek 无 embedding，需单独配 DashScope/Ollama/bge）。

注意：未配置 EMBEDDING_API_KEY 时，RAG 检索阶段会自动跳过，不影响 Web 与 FAQ。
"""
from httpx import Timeout
from openai import OpenAI

from config import config
from logger import get_logger

logger = get_logger("clients.embedding")

_EMBED_TIMEOUT = Timeout(connect=10.0, read=60.0, write=30.0, pool=10.0)


class EmbeddingClient:
    def __init__(self):
        self._client = None

    def ready(self) -> bool:
        return bool(config.EMBEDDING_API_KEY)

    def _get_client(self) -> OpenAI:
        if self._client is None:
            if not self.ready():
                raise RuntimeError("未配置 EMBEDDING_API_KEY")
            self._client = OpenAI(api_key=config.EMBEDDING_API_KEY, base_url=config.EMBEDDING_BASE_URL, timeout=_EMBED_TIMEOUT)
        return self._client

    def embed(self, text: str) -> list[float]:
        resp = self._get_client().embeddings.create(model=config.EMBEDDING_MODEL, input=[text])
        return resp.data[0].embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        resp = self._get_client().embeddings.create(model=config.EMBEDDING_MODEL, input=texts)
        data = {item.index: item.embedding for item in resp.data}
        return [data[i] for i in range(len(texts))]


embedding_client = EmbeddingClient()
