from datetime import datetime, timedelta, timezone

import httpx

from .base import ProviderError, UsageProvider, UsageSnapshot


class AnthropicUsageProvider(UsageProvider):
    """Reads the Anthropic organization usage & cost report API.

    Requires an Admin API key. Docs:
    https://docs.claude.com/en/api/usage-cost-api
    """

    name = "anthropic"
    usage_url = "https://api.anthropic.com/v1/organizations/usage_report/messages"

    async def fetch_usage(self, api_key: str) -> UsageSnapshot:
        starting_at = (datetime.now(timezone.utc) - timedelta(days=1)).strftime(
            "%Y-%m-%dT00:00:00Z"
        )
        headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01"}
        params = {"starting_at": starting_at, "bucket_width": "1d"}

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(self.usage_url, params=params, headers=headers)

        if resp.status_code != 200:
            raise ProviderError(
                f"Anthropic usage API error ({resp.status_code}): {resp.text[:300]}"
            )

        payload = resp.json()
        input_tokens = 0
        output_tokens = 0
        requests = 0
        for bucket in payload.get("data", []):
            for result in bucket.get("results", []):
                input_tokens += result.get("uncached_input_tokens", 0)
                output_tokens += result.get("output_tokens", 0)
                requests += result.get("num_requests", 0)

        return UsageSnapshot(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            requests=requests or None,
            period="last_24h",
            raw=payload,
        )
