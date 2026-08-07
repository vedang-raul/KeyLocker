from .base import ProviderError, UsageProvider, UsageSnapshot


class GeminiUsageProvider(UsageProvider):
    """Placeholder adapter for Google Gemini.

    Google does not expose per-API-key token usage through a simple API-key
    authenticated endpoint; usage lives in Cloud Billing / Cloud Monitoring
    and needs a GCP service account, not a Gemini API key. Wire that up here
    once that integration is scoped.
    """

    name = "gemini"

    async def fetch_usage(self, api_key: str) -> UsageSnapshot:
        raise ProviderError(
            "Gemini usage reporting requires Google Cloud Monitoring "
            "integration and isn't wired up yet."
        )
