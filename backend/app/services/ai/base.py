from abc import ABC, abstractmethod

from app.schemas.ai import AIResponse


class AIProviderError(Exception):
    """Base exception for AI providers."""

    pass


class AIProviderRateLimitError(AIProviderError):
    """Exception when AI provider rate limit is exceeded."""

    pass


class AIContextLengthExceededError(AIProviderError):
    """Exception when context length exceeds model limit."""

    pass


class BaseAIProvider(ABC):
    """Abstract Base Class for AI/LLM providers."""

    def __init__(self, model_name: str = "mock-llm-v1") -> None:
        self.model_name = model_name

    @abstractmethod
    async def generate_completion(self, prompt: str, context: str) -> AIResponse:
        """Generate structured completion with citations."""
        pass

    @abstractmethod
    async def generate_embedding(self, text: str) -> list[float]:
        """Generate vector embedding for text chunk."""
        pass
