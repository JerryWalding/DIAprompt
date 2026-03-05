"""
state.py - Pipeline Session State Manager. Framework: v12.2 Section 5.2

Tracks per-run state across pipeline stages so that each stage can read
and update shared context without passing large argument lists.
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """Mutable state object passed through the pipeline run."""

    run_id: int = None
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Stage outputs
    raw_articles: list = field(default_factory=list)
    scored_articles: list = field(default_factory=list)
    filtered_articles: list = field(default_factory=list)
    aggregated: list = field(default_factory=list)
    brief: dict = field(default_factory=dict)

    # Counters
    article_count: int = 0
    alert_count: int = 0
    claim_count: int = 0
    error_count: int = 0

    # Flags
    completed: bool = False
    status: str = "RUNNING"

    # Arbitrary extras
    metadata: dict = field(default_factory=dict)

    def set(self, key: str, value: Any):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            self.metadata[key] = value
        logger.debug(f"[STATE] {key} updated")

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        return self.metadata.get(key, default)

    def mark_complete(self, status: str = "COMPLETED"):
        self.completed = True
        self.status = status
        logger.info(f"[STATE] Run {self.run_id} marked {status}")

    def summary(self) -> dict:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "status": self.status,
            "article_count": self.article_count,
            "alert_count": self.alert_count,
            "claim_count": self.claim_count,
            "error_count": self.error_count,
            "completed": self.completed,
        }