"""Honcho-style dialectic user modeling — 12 identity slots updated per turn."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .memory import FourLayerMemory

DIMENSIONS = [
    "expertise_level",
    "communication_preference",
    "detail_tolerance",
    "trust_level",
    "topic_affinity",
    "topic_aversion",
    "authority_posture",
    "humor_tolerance",
    "error_response",
    "pacing",
    "channel_preference",
    "current_life_context",
]


@dataclass
class DialecticUpdate:
    dimension: str
    value: str
    confidence: float
    reason: str = ""


class DialecticModel:
    """Rule-based heuristic model. Production swaps for a fine-grained LLM pass."""

    _EXPERT_RX = re.compile(r"\b(i'?m a |i am a |as a )?(senior|principal|staff|lead|phd|engineer|researcher|physician)\b", re.IGNORECASE)
    _NOVICE_RX = re.compile(r"\b(i'?m new to|i don'?t know|first time|explain to me like i'?m)\b", re.IGNORECASE)
    _TERSE_RX = re.compile(r"\b(tldr|keep it short|brief|concise)\b", re.IGNORECASE)
    _EXPANSIVE_RX = re.compile(r"\b(tell me more|explain in detail|elaborate|walk me through)\b", re.IGNORECASE)
    _SKEPTICAL_RX = re.compile(r"\b(are you sure|prove it|citation\??|source\??)\b", re.IGNORECASE)

    def infer(self, text: str) -> list[DialecticUpdate]:
        updates: list[DialecticUpdate] = []
        if self._EXPERT_RX.search(text):
            updates.append(DialecticUpdate("expertise_level", "expert", 0.65, "phrase match"))
        elif self._NOVICE_RX.search(text):
            updates.append(DialecticUpdate("expertise_level", "novice", 0.7, "phrase match"))

        if self._TERSE_RX.search(text):
            updates.append(DialecticUpdate("communication_preference", "terse", 0.7, "phrase match"))
        elif self._EXPANSIVE_RX.search(text):
            updates.append(DialecticUpdate("communication_preference", "expansive", 0.7, "phrase match"))

        if self._SKEPTICAL_RX.search(text):
            updates.append(DialecticUpdate("trust_level", "skeptical", 0.6, "phrase match"))

        return updates

    def apply(self, memory: FourLayerMemory, text: str) -> list[DialecticUpdate]:
        if not memory.dialectic_enabled:
            return []
        updates = self.infer(text)
        for u in updates:
            memory.set_dialectic(u.dimension, u.value, u.confidence)
        return updates

    def summary(self, memory: FourLayerMemory) -> str:
        return memory.dialectic_summary()
