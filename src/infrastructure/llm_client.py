"""LLM client abstraction layer for Ollama and Claude API."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from llama_index.core.llms import LLM
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.ollama import Ollama

from src.config import LLMProvider, get_settings

settings = get_settings()


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    def get_llm(self) -> LLM:
        """Get the LlamaIndex LLM instance."""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text from prompt."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check if LLM service is available."""
        pass


class OllamaClient(BaseLLMClient):
    """Ollama local LLM client."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        model: Optional[str] = None,
    ):
        self.host = host or settings.ollama_host
        self.port = port or settings.ollama_port
        self.model = model or settings.ollama_model
        self._llm: Optional[Ollama] = None

    def get_llm(self) -> Ollama:
        """Get Ollama LLM instance."""
        if self._llm is None:
            self._llm = Ollama(
                model=self.model,
                base_url=f"http://{self.host}:{self.port}",
                request_timeout=120.0,
            )
        return self._llm

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using Ollama."""
        llm = self.get_llm()

        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        response = await llm.acomplete(full_prompt, **kwargs)
        return response.text

    def health_check(self) -> bool:
        """Check if Ollama is available."""
        try:
            import httpx

            response = httpx.get(
                f"http://{self.host}:{self.port}/api/tags",
                timeout=5.0,
            )
            return response.status_code == 200
        except Exception:
            return False


class ClaudeClient(BaseLLMClient):
    """Anthropic Claude API client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.anthropic_model
        self._llm: Optional[Anthropic] = None

    def get_llm(self) -> Anthropic:
        """Get Claude LLM instance."""
        if self._llm is None:
            self._llm = Anthropic(
                api_key=self.api_key,
                model=self.model,
                max_tokens=4096,
            )
        return self._llm

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text using Claude API."""
        llm = self.get_llm()

        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        response = await llm.acomplete(full_prompt, **kwargs)
        return response.text

    def health_check(self) -> bool:
        """Check if Claude API is configured."""
        return bool(self.api_key)


class LLMClient:
    """Unified LLM client that routes to appropriate backend."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or settings.llm_provider
        self._client: Optional[BaseLLMClient] = None

    @property
    def client(self) -> BaseLLMClient:
        """Get the appropriate LLM client based on provider."""
        if self._client is None:
            if self.provider == LLMProvider.OLLAMA:
                self._client = OllamaClient()
            elif self.provider == LLMProvider.ANTHROPIC:
                self._client = ClaudeClient()
            else:
                raise ValueError(f"Unknown LLM provider: {self.provider}")
        return self._client

    def get_llm(self) -> LLM:
        """Get the underlying LlamaIndex LLM instance."""
        return self.client.get_llm()

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate text from prompt."""
        return await self.client.generate(prompt, system_prompt, **kwargs)

    def health_check(self) -> bool:
        """Check if LLM service is available."""
        return self.client.health_check()


def get_llm_client(provider: Optional[LLMProvider] = None) -> LLMClient:
    """Factory function to get LLM client."""
    return LLMClient(provider)
