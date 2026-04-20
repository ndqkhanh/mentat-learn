"""Mentat-Learn: self-improving personal assistant.

Public API:
  - MentatAgent: orchestrates a single user session across channels
  - FourLayerMemory: procedural / facts / session / dialectic
  - SkillLibrary: cache-aware, versioned skill store + SkillExtractor
  - Gateway: channel adapter coordinator
  - CronScheduler: time-based automations
  - SelfEvaluator: periodic skill + persona drift audit
"""
from __future__ import annotations

from .cron import CronScheduler, Schedule
from .dialectic import DialecticModel
from .gateway import ChannelAdapter, Gateway, InMemoryChannel, InboundMessage, OutboundMessage
from .loop import MentatAgent, TurnResult
from .memory import DialecticEntry, Fact, FourLayerMemory, ProceduralMemory, SessionMemory
from .models import ConsentFlags, SkillRecord, UserProfile
from .privacy import PIIRedactor, PrivacyScope
from .self_eval import SelfEvaluator, SelfEvalReport
from .sessions import Session, SessionStore
from .skills import SkillExtractor, SkillLibrary

__all__ = [
    "ChannelAdapter",
    "ConsentFlags",
    "CronScheduler",
    "DialecticEntry",
    "DialecticModel",
    "Fact",
    "FourLayerMemory",
    "Gateway",
    "InboundMessage",
    "InMemoryChannel",
    "MentatAgent",
    "OutboundMessage",
    "PIIRedactor",
    "PrivacyScope",
    "ProceduralMemory",
    "Schedule",
    "SelfEvalReport",
    "SelfEvaluator",
    "Session",
    "SessionMemory",
    "SessionStore",
    "SkillExtractor",
    "SkillLibrary",
    "SkillRecord",
    "TurnResult",
    "UserProfile",
]
