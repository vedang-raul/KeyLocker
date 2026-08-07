from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class UsageSnapshot:
    """Normalized usage numbers, regardless of which provider they came from."""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    requests: Optional[int] = None
    period: Optional[str] = None
    raw: dict[str, Any] = field(default_factory=dict)


class ProviderError(Exception):
    """Raised when a provider's usage API can't be reached or parsed."""


class UsageProvider(ABC):
    """Adapter contract: given a raw API key, return normalized usage.

    To add a new provider, subclass this, set `name`, implement
    `fetch_usage`, and register an instance in `providers/registry.py`.
    """

    name: str

    @abstractmethod
    async def fetch_usage(self, api_key: str) -> UsageSnapshot:
        ...
