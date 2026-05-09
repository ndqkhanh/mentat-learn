"""Four-layer memory: procedural (skills) / facts / session / dialectic.

The procedural layer is thin here and owned by the SkillLibrary; this module
owns facts, session state, and the dialectic user model.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Fact:
    id: str
    content: str
    kind: str = "fact"                    # fact | preference | exclusion | reference
    actor: str = "agent"
    confidence: float = 1.0
    created_at: float = field(default_factory=time.time)
    last_used_at: float = 0.0
    expires_at: Optional[float] = None
    source_channel: Optional[str] = None

    def expired(self) -> bool:
        return self.expires_at is not None and self.expires_at < time.time()


@dataclass
class DialecticEntry:
    """A slot in the Honcho-style user-agent relationship model."""
    dimension: str                        # e.g., "expertise_level", "communication_preference"
    value: str
    confidence: float = 0.5
    updated_at: float = field(default_factory=time.time)


@dataclass
class SessionMemory:
    """Per-session working context."""
    session_id: str
    channel: str
    turns: list[dict] = field(default_factory=list)   # list of {"role","text","ts"}
    established_facts: list[str] = field(default_factory=list)
    intent_arc: str = ""
    created_at: float = field(default_factory=time.time)
    last_activity_at: float = field(default_factory=time.time)


class ProceduralMemory:
    """Thin view — skills are owned by SkillLibrary; this is just an aliasing shim."""

    def __init__(self, library) -> None:  # SkillLibrary (avoid import cycle)
        self._lib = library

    def count(self) -> int:
        return len(self._lib.all())

    def describe(self) -> list[str]:
        return [f"{s.name}: {s.description}" for s in self._lib.all()]


class FactStore:
    """Indexed-by-kind + FTS-ish (naive token) fact store."""

    def __init__(self) -> None:
        self._by_id: dict[str, Fact] = {}

    def add(self, fact: Fact) -> Fact:
        self._by_id[fact.id] = fact
        return fact

    def add_new(
        self,
        content: str,
        *,
        kind: str = "fact",
        actor: str = "agent",
        confidence: float = 1.0,
        source_channel: Optional[str] = None,
        expires_at: Optional[float] = None,
    ) -> Fact:
        f = Fact(
            id=uuid.uuid4().hex[:12],
            content=content,
            kind=kind,
            actor=actor,
            confidence=confidence,
            source_channel=source_channel,
            expires_at=expires_at,
        )
        return self.add(f)

    def all(self, *, include_expired: bool = False) -> list[Fact]:
        if include_expired:
            return list(self._by_id.values())
        return [f for f in self._by_id.values() if not f.expired()]

    def of_kind(self, kind: str) -> list[Fact]:
        return [f for f in self.all() if f.kind == kind]

    def search(self, query: str, *, limit: int = 10) -> list[Fact]:
        q_tokens = [t for t in query.lower().split() if len(t) > 2]
        scored: list[tuple[int, Fact]] = []
        for f in self.all():
            text = f.content.lower()
            hits = sum(1 for t in q_tokens if t in text)
            if hits:
                scored.append((hits, f))
        scored.sort(key=lambda x: (-x[0], -x[1].created_at))
        results = [f for _, f in scored[:limit]]
        now = time.time()
        for f in results:
            f.last_used_at = now
        return results

    def delete(self, fact_id: str) -> bool:
        return self._by_id.pop(fact_id, None) is not None

    def clear(self) -> None:
        self._by_id.clear()


class FourLayerMemory:
    """Groups the four layers; each is independently addressable."""

    def __init__(self, library, *, dialectic_enabled: bool = False) -> None:
        self.procedural = ProceduralMemory(library)
        self.facts = FactStore()
        self.sessions: dict[str, SessionMemory] = {}
        self.dialectic: dict[str, DialecticEntry] = {}
        self.dialectic_enabled = dialectic_enabled

    # -- session helpers --------------------------------------------------------

    def get_or_create_session(self, session_id: str, channel: str) -> SessionMemory:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMemory(session_id=session_id, channel=channel)
        return self.sessions[session_id]

    def append_turn(self, session_id: str, channel: str, role: str, text: str) -> None:
        sess = self.get_or_create_session(session_id, channel)
        sess.turns.append({"role": role, "text": text, "ts": time.time()})
        sess.last_activity_at = time.time()

    # -- dialectic helpers ------------------------------------------------------

    def set_dialectic(self, dimension: str, value: str, confidence: float = 0.5) -> None:
        if not self.dialectic_enabled:
            return
        self.dialectic[dimension] = DialecticEntry(
            dimension=dimension, value=value, confidence=confidence
        )

    def dialectic_summary(self) -> str:
        if not self.dialectic_enabled or not self.dialectic:
            return ""
        return "; ".join(f"{d.dimension}={d.value}" for d in self.dialectic.values())

    # -- purge ------------------------------------------------------------------

    def forget_session(self, session_id: str) -> bool:
        return self.sessions.pop(session_id, None) is not None

    def forget_all(self) -> None:
        self.facts.clear()
        self.sessions.clear()
        self.dialectic.clear()
