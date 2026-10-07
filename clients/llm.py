"""大模型生成客户端（OpenAI 兼容协议，默认 DeepSeek，懒加载）。"""
from httpx import Timeout
from openai import OpenAI

from config import config
from logger import get_logger

logger = get_logger("clients.llm")

# 连接10s / 读90s / 写30s：DeepSeek 高峰期可能较慢，超时后快速失败而非无限挂起
_LLM_TIMEOUT = Timeout(connect=10.0, read=90.0, write=30.0, pool=10.0)


class LLMClient:
    def __init__(self):
        self._client = None

    def ready(self) -> bool:
        return bool(config.LLM_API_KEY)

    def _get_client(self) -> OpenAI:
        if self._client is None:
            if not self.ready():
                raise RuntimeError("未配置 DEEPSEEK_API_KEY / LLM_API_KEY")
            self._client = OpenAI(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL, timeout=_LLM_TIMEOUT)
        return self._client

    def chat(self, prompt: str, temperature: float = 0.3, max_tokens: int = 1024) -> str:
        """单轮生成。"""
        if not self.ready():
            return "（尚未配置 DEEPSEEK_API_KEY，请先设置环境变量后重试）"
        resp = self._get_client().chat.completions.create(
            model=config.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""


llm_client = LLMClient()
