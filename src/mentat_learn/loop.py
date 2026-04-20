"""MentatAgent — composes gateway, memory, skills, privacy, dialectic, self-eval."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .dialectic import DialecticModel, DialecticUpdate
from .gateway import Gateway, InboundMessage, OutboundMessage
from .memory import FourLayerMemory
from .models import UserProfile
from .privacy import PrivacyScope
from .self_eval import SelfEvaluator
from .sessions import SessionStore
from .skills import SkillLibrary, SkillMatch


@dataclass
class TurnResult:
    reply: str
    session_id: str
    channel: str
    matched_skills: list[SkillMatch] = field(default_factory=list)
    memory_writes: int = 0
    dialectic_updates: list[DialecticUpdate] = field(default_factory=list)
    pii_redactions: int = 0


class MentatAgent:
    """Full per-user agent composing all blocks."""

    def __init__(
        self,
        profile: UserProfile,
        *,
        gateway: Optional[Gateway] = None,
        library: Optional[SkillLibrary] = None,
        memory: Optional[FourLayerMemory] = None,
        sessions: Optional[SessionStore] = None,
        dialectic: Optional[DialecticModel] = None,
    ) -> None:
        self.profile = profile
        self.gateway = gateway or Gateway()
        self.library = library or SkillLibrary()
        self.memory = memory or FourLayerMemory(self.library, dialectic_enabled=False)
        self.sessions = sessions or SessionStore()
        self.dialectic = dialectic or DialecticModel()
        self.privacy = PrivacyScope(profile)
        self.evaluator = SelfEvaluator(self.library, self.memory)

    # -- single-turn path -------------------------------------------------------

    def handle(self, msg: InboundMessage) -> TurnResult:
        # 1. Resolve session (get_or_create bumps if exists)
        sess = self.sessions.get_or_create(
            user_id=msg.user_id, channel=msg.channel, session_id=msg.session_id,
        )
        self.sessions.bump(sess.id)

        # 2. Privacy: scrub inbound before memory
        scrub = self.privacy.scrub(msg.text, msg.channel)
        redactions = len(scrub.redactions)
        safe_text = scrub.text

        # 3. Append to session memory (always) + persistent memory (if consented)
        self.memory.append_turn(sess.id, msg.channel, role="user", text=safe_text)
        mem_writes = 0
        if self.privacy.can_write_memory(msg.channel):
            # Very small extractor: if user says "I prefer …", record as preference
            if "i prefer" in msg.text.lower() or "i like" in msg.text.lower():
                self.memory.facts.add_new(
                    content=safe_text,
                    kind="preference",
                    actor="user",
                    source_channel=msg.channel,
                )
                mem_writes += 1

        # 4. Dialectic modeling (if consented)
        dialectic_updates: list[DialecticUpdate] = []
        if self.privacy.can_model_dialectic(msg.channel):
            self.memory.dialectic_enabled = True
            dialectic_updates = self.dialectic.apply(self.memory, msg.text)

        # 5. Skill match + compose reply
        matches = self.library.match(msg.text, top_k=3)
        if matches:
            skill = matches[0].skill
            self.library.record_use(skill.id, success=True)
            body = self.library.body(skill.id) or ""
            reply = self._render_skill_reply(skill.name, body, safe_text)
        else:
            reply = self._render_first_principles_reply(safe_text)

        # 6. Append assistant turn
        self.memory.append_turn(sess.id, msg.channel, role="assistant", text=reply)

        # 7. Emit outbound via gateway adapter (if registered)
        adapter = self.gateway.get(msg.channel)
        if adapter is not None:
            adapter.send(OutboundMessage(
                in_reply_to=msg.id,
                user_id=msg.user_id,
                session_id=sess.id,
                channel=msg.channel,
                text=reply,
            ))

        # 8. Self-eval bookkeeping
        self.evaluator.note_task()

        return TurnResult(
            reply=reply,
            session_id=sess.id,
            channel=msg.channel,
            matched_skills=matches,
            memory_writes=mem_writes,
            dialectic_updates=dialectic_updates,
            pii_redactions=redactions,
        )

    # -- rendering --------------------------------------------------------------

    def _render_skill_reply(self, skill_name: str, body: str, user_text: str) -> str:
        dial = self.dialectic.summary(self.memory)
        dial_snippet = f"\n\n(dialectic: {dial})" if dial else ""
        return (
            f"[skill={skill_name}]\n"
            f"Understood: {user_text.strip()[:140]}\n"
            f"{body.splitlines()[0] if body else ''}{dial_snippet}"
        )

    def _render_first_principles_reply(self, user_text: str) -> str:
        dial = self.dialectic.summary(self.memory)
        dial_snippet = f"\n(dialectic: {dial})" if dial else ""
        return (
            f"[first-principles]\n"
            f"I don't have a skill for that yet. Received: {user_text.strip()[:200]}"
            f"{dial_snippet}"
        )
