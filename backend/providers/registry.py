from .base import ProviderError, UsageProvider
from .anthropic_provider import AnthropicUsageProvider
from .gemini_provider import GeminiUsageProvider
from .groq_provider import GroqUsageProvider
from .grok_provider import GrokUsageProvider
from .openai_provider import OpenAIUsageProvider

_PROVIDERS: dict[str, UsageProvider] = {
    provider.name: provider
    for provider in (
        OpenAIUsageProvider(),
        AnthropicUsageProvider(),
        GeminiUsageProvider(),
        GrokUsageProvider(),
        GroqUsageProvider(),
    )
}


def get_provider(name: str) -> UsageProvider:
    try:
        return _PROVIDERS[name]
    except KeyError:
        raise ProviderError(f"Unsupported provider: {name}")


def list_providers() -> list[str]:
    return list(_PROVIDERS.keys())
