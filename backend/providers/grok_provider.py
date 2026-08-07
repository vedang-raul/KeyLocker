from .base import ProviderError, UsageProvider, UsageSnapshot


class GrokUsageProvider(UsageProvider):
    """Placeholder adapter for xAI's Grok.

    xAI does not currently publish a stable organization-level usage API.
    Wire this up once one is available.
    """

    name = "grok"

    async def fetch_usage(self, api_key: str) -> UsageSnapshot:
        raise ProviderError("Grok usage reporting isn't available yet.")
