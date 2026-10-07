"""全局配置：从 .env 读取。"""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # 服务
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))

    # MySQL
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "root")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "tech_rag")

    # Milvus
    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "127.0.0.1")
    MILVUS_PORT: int = int(os.getenv("MILVUS_PORT", "19530"))
    MILVUS_COLLECTION: str = os.getenv("MILVUS_COLLECTION", "tech_rag_docs")
    MILVUS_DIM: int = int(os.getenv("MILVUS_DIM", "1024"))

    # 大模型（DeepSeek 优先；OpenAI 兼容协议）
    LLM_API_KEY: str = os.getenv("DEEPSEEK_API_KEY") or os.getenv("LLM_API_KEY", "")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "deepseek-chat")

    # 向量化（DeepSeek 无 embedding 接口，单独配置，默认 DashScope 兼容；可改本地 Ollama/bge）
    EMBEDDING_API_KEY: str = os.getenv("EMBEDDING_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_BASE_URL: str = os.getenv("EMBEDDING_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")

    # 联网
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")

    # 检索参数
    FAQ_THRESHOLD: float = float(os.getenv("FAQ_THRESHOLD", "0.60"))
    RAG_THRESHOLD: float = float(os.getenv("RAG_THRESHOLD", "0.45"))
    TOP_K: int = int(os.getenv("TOP_K", "5"))

    @property
    def mysql_url(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"
        )


config = Config()
