from typing import Optional

from pydantic import BaseModel, ConfigDict


class MonitorReg(BaseModel):
    provider: str
    label: str
    api_key: str


class MonitorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    monitor_id: int
    provider: str
    label: str
    masked_key: str


class UsageResponse(BaseModel):
    monitor_id: int
    label: str
    provider: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    requests: Optional[int] = None
    period: Optional[str] = None
