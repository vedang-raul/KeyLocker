import time

import httpx

from .base import ProviderError, UsageProvider, UsageSnapshot


class OpenAIUsageProvider(UsageProvider):
    """Reads the OpenAI organization usage API.

    Requires an Admin API key (sk-admin-...), not a regular project key.
    Docs: https://platform.openai.com/docs/api-reference/usage
    """

    name = "openai"
    usage_url = "https://api.openai.com/v1/organization/usage/completions"

    async def fetch_usage(self, api_key: str) -> UsageSnapshot:
        start_time = int(time.time()) - 86400  # last 24h
        params = {"start_time": start_time, "bucket_width": "1d"}
        headers = {"Authorization": f"Bearer {api_key}"}

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(self.usage_url, params=params, headers=headers)

        if resp.status_code != 200:
            raise ProviderError(
                f"OpenAI usage API error ({resp.status_code}): {resp.text[:300]}"
            )

        payload = resp.json()
        input_tokens = 0
        output_tokens = 0
        requests = 0
        for bucket in payload.get("data", []):
            for result in bucket.get("results", []):
                input_tokens += result.get("input_tokens", 0)
                output_tokens += result.get("output_tokens", 0)
                requests += result.get("num_model_requests", 0)

        return UsageSnapshot(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            requests=requests,
            period="last_24h",
            raw=payload,
        )
