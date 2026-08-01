from pydantic import BaseModel, Field
from typing import Any

class Requirement(BaseModel):
    feature_name: str = ""

    business_goal: str = ""

    actors: list[str] = Field(default_factory=list)

    user_story: str = ""

    ui_components: list[str] = Field(default_factory=list)

    ui_validations: list[str] = Field(default_factory=list)

    workflows: list[str] = Field(default_factory=list)

    api_endpoints: list[str] = Field(default_factory=list)

    business_rules: list[str] = Field(default_factory=list)

    assumptions: list[str] = Field(default_factory=list)