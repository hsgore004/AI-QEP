from typing import Any, Literal

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    system_prompt: str
    user_prompt: str

    model: str | None = None

    temperature: float = Field(
        default=0.2,
        ge=0,
        le=2,
        description="Sampling temperature."
    )

    max_tokens: int = Field(
        default=4000,
        gt=0
    )

    response_model: type[Any] | None = None

    attachments: list[str] = Field(default_factory=list)

    # NEW
    response_format: Literal["text", "json"] = "text"