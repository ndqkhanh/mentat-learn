"""SkillLibrary + SkillExtractor — the closed learning loop.

- Library stores versioned SkillRecord objects.
- Extractor runs at end-of-task, drafts a SKILL.md, evaluates it, commits on pass.
- Compression merges co-occurring skills into higher-order composites.
- Cache-aware body loading (in-memory LRU).
"""
from __future__ import annotations

import math
import re
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Optional

from .models import SkillRecord

_TOKEN_RX = re.compile(r"[a-zA-Z0-9']+")
_STOPWORDS = {
    "a","an","the","is","are","was","were","be","been","being","and","or","but",
    "if","then","to","of","in","on","at","for","with","by","as","it","this","that",
    "these","those","my","your","our","their","me","us","them","i","you","we","they",
    "what","who","when","where","how","why","do","does","did","will","would","can",
}


def _bow(text: str) -> dict[str, float]:
    counts: dict[str, int] = {}
    for tok in _TOKEN_RX.findall(text.lower()):
        if tok in _STOPWORDS or len(tok) < 2:
            continue
        counts[tok] = counts.get(tok, 0) + 1
    if not counts:
        return {}
    norm = math.sqrt(sum(v * v for v in counts.values()))
    return {k: v / norm for k, v in counts.items()}


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    return sum(a[k] * b.get(k, 0.0) for k in a)


@dataclass
class SkillMatch:
    skill: SkillRecord
    score: float


class SkillLibrary:
    """Cache-aware skill library. Skills indexed by description embedding."""

    def __init__(self, *, body_cache_size: int = 50) -> None:
        self._skills: dict[str, SkillRecord] = {}
        self._embeddings: dict[str, dict[str, float]] = {}
        self._body_cache: "OrderedDict[str, str]" = OrderedDict()
        self._body_cache_size = body_cache_size
        self._co_occurrence: dict[tuple[str, ...], int] = {}

    # -- CRUD -------------------------------------------------------------------

    def register(self, skill: SkillRecord) -> SkillRecord:
        if any(s.name == skill.name and s.subsumed_by is None for s in self._skills.values()):
            raise ValueError(f"skill name {skill.name!r} already exists")
        self._skills[skill.id] = skill
        self._embeddings[skill.id] = _bow(skill.description)
        self._body_cache[skill.id] = skill.body_md
        self._evict()
        return skill

    def update(self, skill: SkillRecord) -> SkillRecord:
        self._skills[skill.id] = skill
        self._embeddings[skill.id] = _bow(skill.description)
        self._body_cache[skill.id] = skill.body_md
        self._evict()
        return skill

    def get(self, skill_id: str) -> Optional[SkillRecord]:
        return self._skills.get(skill_id)

    def all(self, include_subsumed: bool = True) -> list[SkillRecord]:
        return [s for s in self._skills.values() if include_subsumed or s.subsumed_by is None]

    def disable(self, skill_id: str) -> None:
        self._skills.pop(skill_id, None)
        self._embeddings.pop(skill_id, None)
        self._body_cache.pop(skill_id, None)

    # -- routing ----------------------------------------------------------------

    def match(self, query: str, *, top_k: int = 3, threshold: float = 0.25) -> list[SkillMatch]:
        q = _bow(query)
        scored: list[SkillMatch] = []
        for sid, emb in self._embeddings.items():
            skill = self._skills[sid]
            if skill.subsumed_by is not None:
                continue
            sim = _cosine(q, emb)
            if sim < threshold:
                continue
            # blend similarity + log(use_count) + success rate bonus
            sr = skill.success_rate if skill.success_rate is not None else 0.5
            score = 0.6 * sim + 0.2 * sr + 0.2 * (math.log(1 + skill.use_count) / math.log(50))
            scored.append(SkillMatch(skill=skill, score=score))
        scored.sort(key=lambda m: -m.score)
        return scored[:top_k]

    def body(self, skill_id: str) -> Optional[str]:
        if skill_id in self._body_cache:
            # LRU touch
            self._body_cache.move_to_end(skill_id)
            return self._body_cache[skill_id]
        skill = self._skills.get(skill_id)
        if skill is None:
            return None
        self._body_cache[skill_id] = skill.body_md
        self._evict()
        return skill.body_md

    def _evict(self) -> None:
        while len(self._body_cache) > self._body_cache_size:
            self._body_cache.popitem(last=False)

    # -- usage stats ------------------------------------------------------------

    def record_use(self, skill_id: str, *, success: bool) -> None:
        skill = self._skills.get(skill_id)
        if skill is None:
            return
        skill.use_count += 1
        if success:
            skill.success_count += 1
        skill.last_updated = time.time()

    def record_co_occurrence(self, skill_ids: tuple[str, ...]) -> None:
        if len(skill_ids) < 2:
            return
        key = tuple(sorted(skill_ids))
        self._co_occurrence[key] = self._co_occurrence.get(key, 0) + 1

    def co_occurrence_counts(self) -> dict[tuple[str, ...], int]:
        return dict(self._co_occurrence)


class SkillExtractor:
    """End-of-task pattern miner → new SkillRecord draft.

    MVP: rule-based — we detect repeatable shapes from a bounded "task trace"
    (sequence of tool invocations + outcomes). Production swaps in an LLM pass.
    """

    MIN_STEPS_FOR_SKILL = 2
    MIN_CO_OCCURRENCE_FOR_COMPRESSION = 3

    def __init__(self, library: SkillLibrary) -> None:
        self.library = library

    def extract(
        self,
        *,
        task_summary: str,
        tool_sequence: list[str],
        outcome: str,
    ) -> Optional[SkillRecord]:
        """Return a new SkillRecord if the trace looks reusable; else None."""
        if outcome != "success":
            return None
        if len(tool_sequence) < self.MIN_STEPS_FOR_SKILL:
            return None
        # Require that the tool sequence has at least 2 distinct tools
        if len(set(tool_sequence)) < 2:
            return None

        name = _slug(task_summary, fallback=f"skill-{int(time.time())}")
        existing = [s for s in self.library.all() if s.name == name]
        if existing:
            # refine existing → bump version, update body
            s = existing[0]
            s.version += 1
            s.body_md = self._draft_body(task_summary, tool_sequence, outcome)
            s.last_updated = time.time()
            self.library.update(s)
            return s

        skill = SkillRecord(
            name=name,
            description=task_summary[:120],
            body_md=self._draft_body(task_summary, tool_sequence, outcome),
            required_tools=list(dict.fromkeys(tool_sequence)),  # dedup preserve order
        )
        return self.library.register(skill)

    def compress(self) -> Optional[SkillRecord]:
        """Find a co-occurring cluster ≥ N times and create a composite skill."""
        for skill_ids, count in self.library.co_occurrence_counts().items():
            if count < self.MIN_CO_OCCURRENCE_FOR_COMPRESSION:
                continue
            bases = [self.library.get(sid) for sid in skill_ids]
            if any(b is None or b.subsumed_by is not None for b in bases):
                continue
            comp_name = "+".join(b.name for b in bases if b)
            comp_desc = "Composite: " + " → ".join(b.description for b in bases if b)
            tools = []
            for b in bases:
                if b:
                    tools.extend(b.required_tools)
            composite = SkillRecord(
                name=comp_name,
                description=comp_desc[:240],
                body_md="\n\n".join((b.body_md if b else "") for b in bases),
                required_tools=list(dict.fromkeys(tools)),
            )
            registered = self.library.register(composite)
            # Mark base skills as subsumed (still callable, just de-preferred)
            for b in bases:
                if b:
                    b.subsumed_by = registered.id
                    self.library.update(b)
            return registered
        return None

    @staticmethod
    def _draft_body(task_summary: str, tool_sequence: list[str], outcome: str) -> str:
        steps = "\n".join(f"{i+1}. Call `{tool}`" for i, tool in enumerate(tool_sequence))
        return (
            f"# Procedure\n\n**Goal:** {task_summary}\n\n"
            f"## Steps\n{steps}\n\n"
            f"## Learnings\n- Last outcome: {outcome}\n"
        )


def _slug(text: str, *, fallback: str) -> str:
    tokens = _TOKEN_RX.findall(text.lower())
    tokens = [t for t in tokens if t not in _STOPWORDS and len(t) > 2]
    if not tokens:
        return fallback
    return "-".join(tokens[:4])
