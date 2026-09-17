"""LLM 客户端（OpenAI 兼容协议，同步实现）

- 根据 settings 解析 provider / key / base_url / model。
- 未配置 Key 时 available=False，节点捕获异常后自动降级到规则引擎。
- 提供 LangChain 风格 agenerate()（返回 .generations[0][0].text）以兼容文档节点代码，
  同时提供直接的 complete() 便捷方法（同步）。
"""
from typing import List, Optional

from app.config import settings
import logging

logger = logging.getLogger(__name__)


class _Text:
    def __init__(self, text: str):
        self.text = text


class _LLMResult:
    def __init__(self, texts: List[str]):
        # generations[i][0].text
        self.generations = [[_Text(t)] for t in texts]


class LLMClient:
    def __init__(self):
        cfg = settings.resolved_llm
        self.provider = cfg["provider"]
        self.api_key = cfg["api_key"]
        self.base_url = cfg["base_url"]
        self.model = cfg["model"]
        self.available = bool(self.api_key)
        self._client = None
        if self.available:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except Exception as e:  # pragma: no cover
                logger.warning("LLM 客户端初始化失败，将降级规则引擎: %s", e)
                self.available = False

    def complete(self, prompt: str, temperature: Optional[float] = None,
                 max_tokens: Optional[int] = None) -> str:
        if not self.available or self._client is None:
            raise RuntimeError("LLM 未配置（无 API Key），请使用规则引擎模式")
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
            max_tokens=max_tokens if max_tokens is not None else settings.LLM_MAX_TOKENS,
        )
        return resp.choices[0].message.content or ""

    def agenerate(self, prompts: List[str], **kwargs) -> _LLMResult:
        """LangChain 风格：输入 prompt 列表，返回 .generations[i][0].text"""
        return _LLMResult([self.complete(p, **kwargs) for p in prompts])


_client_singleton: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _client_singleton
    if _client_singleton is None:
        _client_singleton = LLMClient()
    return _client_singleton
