from .base import ProviderError, UsageProvider, UsageSnapshot


class GroqUsageProvider(UsageProvider):
    """Placeholder adapter for Groq (console.groq.com).

    As of writing, Groq's API only exposes per-request token counts inside
    individual chat completion responses (prompt_tokens/completion_tokens).
    There is no documented organization-level usage or billing endpoint to
    poll, unlike OpenAI/Anthropic. Wire this up once Groq ships one.
    """

    name = "groq"

    async def fetch_usage(self, api_key: str) -> UsageSnapshot:
        raise ProviderError(
            "Groq doesn't expose an organization usage API yet — only "
            "per-request token counts are available, not an aggregate "
            "endpoint to poll."
        )
