"""Mentat-Learn skills adapter — AutoSkill dialogue extraction per user.

Cross-channel persona aggregation lives here: incoming dialogue from any
channel feeds the same `DialogueExtractor`; channel attribution lives in
provenance, never in the rendered skill body. Right-to-erasure cascades
delete every skill in the user's namespace.

This is the *new* harness_skills-based adapter; it sits beside the older
in-tree `mentat_learn.skills.SkillLibrary` (which keeps backing the
existing `test_skills.py` suite).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from harness_skills import SkillRecord
from harness_skills.extract import DialogueExtractor, ExtractionContext
from harness_skills.store import SkillBank

# Channel identifiers we never want surfacing in skill bodies (BL-MENTAT-SKILL-CROSS-CHANNEL).
_CHANNEL_RE = re.compile(
    r"(?i)(\bslack\b|\bwhatsapp\b|\btelegram\b|\bimessage\b|"
    r"@[A-Za-z0-9_]{3,}\.slack\b|\+\d{7,}|\bgmail\b|\bsms\b)"
)


def channel_leak_gate(text: str) -> bool:
    """Return True iff text is safe (no channel identifiers leaked)."""
    return _CHANNEL_RE.search(text or "") is None


@dataclass
class MentatDialogueExtractor:
    extractor: DialogueExtractor

    @classmethod
    def default(cls) -> MentatDialogueExtractor:
        return cls(extractor=DialogueExtractor(family="extractor-mentat"))

    def from_channel(self, turns: list[dict], *, user_id: str, channel_id: str,
                     session_id: str, consent: bool = True) -> list[SkillRecord]:
        """Extract per-user skills; drop anything that leaks channel id."""
        if not consent:                                          # BL-MENTAT-SKILL-CONSENT
            return []
        records = self.extractor.extract(
            turns,
            context=ExtractionContext(session_id=session_id, user_id=user_id,
                                      program_id=channel_id),
        )
        return [r for r in records if channel_leak_gate(r.skill.prompt)]


@dataclass
class MentatSkillBank:
    bank: SkillBank

    @classmethod
    def for_user(cls, root: Path | str, user_id: str) -> MentatSkillBank:
        return cls(bank=SkillBank(root=root, namespace=f"Users/{user_id}"))

    def erase(self) -> int:
        """Cascade-delete every skill in the user namespace.

        Implements ``BL-MENTAT-SKILL-CONSENT`` right-to-erasure: any
        deletion request walks the user namespace and removes every
        SKILL.md, leaving a tombstone in `provenance.jsonl`.
        """
        user_dir = self.bank.active_dir
        deleted = 0
        if user_dir.exists():
            for skill_dir in user_dir.iterdir():
                if not skill_dir.is_dir():
                    continue
                md = skill_dir / "SKILL.md"
                if md.exists():
                    md.unlink()
                    deleted += 1
                prov = skill_dir / "provenance.jsonl"
                with prov.open("a", encoding="utf-8") as fh:
                    fh.write('{"event":"erase","reason":"right-to-erasure"}\n')
        return deleted


__all__ = ["MentatDialogueExtractor", "MentatSkillBank", "channel_leak_gate"]
