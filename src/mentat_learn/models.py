"""Mentat-Learn data model."""
from __future__ import annotations

import time
import uuid
from typing import Optional

from pydantic import BaseModel, Field


class ConsentFlags(BaseModel):
    """Per-channel consent controls. Default is safest: everything off."""

    persistent_memory: bool = False
    cross_channel_share: bool = False
    pii_opt_in: bool = False
    dialectic_modeling: bool = False
    scheduled_automations: bool = False


class UserProfile(BaseModel):
    """Identity + per-channel consent + SOUL.md persona partition."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    soul_md: str = (
        "You are Mentat, a terse personal assistant. "
        "Respect user time. Cite sources. Never invent."
    )
    channels_enabled: dict[str, ConsentFlags] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class SkillRecord(BaseModel):
    """A reusable procedure written as markdown. agentskills.io-compatible."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str
    description: str                       # routing hint (one-line)
    body_md: str                           # full procedure
    required_tools: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    version: int = 1
    use_count: int = 0
    success_count: int = 0
    subsumed_by: Optional[str] = None
    source: str = "extracted"              # extracted | imported | user-authored
    last_updated: float = Field(default_factory=time.time)

    @property
    def success_rate(self) -> Optional[float]:
        if self.use_count == 0:
            return None
        return self.success_count / self.use_count
