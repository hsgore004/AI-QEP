from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass
class Artifact:
    """
    Represents one knowledge artifact produced by a QA Brain stage.
    """

    # Unique identity
    id: str = field(default_factory=lambda: str(uuid4()))

    # Context
    application: str = ""
    module: str = ""
    stage: str = ""

    # Lineage
    parent_id: str | None = None
    source: str = "documentation"

    # Quality
    confidence: float = 0.0
    approved: bool = False

    # Versioning
    version: int = 1

    # Audit
    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    # LLM metadata
    model: str = ""
    prompt_version: str = "1.0"

    # Actual artifact payload
    data: Any = field(default_factory=dict)