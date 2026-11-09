from functools import lru_cache

from ai.providers.base import ImageGenerationProvider, ProviderError
from core.config import AI_PROVIDER, EMERGENT_LLM_KEY, GENERATION_TIMEOUT_S, IMAGE_MODEL


@lru_cache(maxsize=1)
def get_provider() -> ImageGenerationProvider:
    if AI_PROVIDER == "gemini" and EMERGENT_LLM_KEY:
        from ai.providers.gemini import GeminiImageProvider
        return GeminiImageProvider(EMERGENT_LLM_KEY, IMAGE_MODEL, GENERATION_TIMEOUT_S)
    from ai.providers.mock import MockImageProvider
    return MockImageProvider()


__all__ = ["get_provider", "ImageGenerationProvider", "ProviderError"]
