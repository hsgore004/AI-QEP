from typing import Any

from pydantic import BaseModel
from pydantic import Field

class LLMResponse(BaseModel):
    content: str
    model: str

    prompt_tokens: int = Field(
    default=0,
    ge=0
    )
    completion_tokens: int = Field(
    default=0,
    ge=0
    )
    total_tokens: int = Field(
    default=0,
    ge=0
    )

    latency: float = Field(
    default=0.0,
    ge=0
    )

    success: bool = True

    finish_reason: str | None = None

    error: str | None = None