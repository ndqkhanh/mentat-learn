"""Mentat-Learn skills-adapter smoke test."""
from __future__ import annotations

from harness_skills import Skill, SkillRecord, TrustTier
from mentat_learn.skills_adapter import (
    MentatDialogueExtractor,
    MentatSkillBank,
    channel_leak_gate,
)


def test_channel_leak_gate_blocks_identifiers() -> None:
    assert not channel_leak_gate("Always reply in Slack with markdown")
    assert not channel_leak_gate("Tell @alice.slack to ping me")
    assert not channel_leak_gate("Forward to +12025550123")
    assert channel_leak_gate("Always render replies in markdown")


def test_consent_off_returns_empty() -> None:
    ext = MentatDialogueExtractor.default()
    turns = [{"role": "user", "content": "Always reply in markdown"}]
    out = ext.from_channel(turns, user_id="u1", channel_id="c1",
                            session_id="s1", consent=False)
    assert out == []


def test_consent_on_extracts_and_strips_channel_leaks() -> None:
    ext = MentatDialogueExtractor.default()
    turns = [
        {"role": "user", "content": "Always render replies in markdown"},
        {"role": "user", "content": "Always reply in Slack threads"},  # channel leak
    ]
    out = ext.from_channel(turns, user_id="u1", channel_id="slack-1",
                            session_id="s1", consent=True)
    assert out
    assert all(channel_leak_gate(r.skill.prompt) for r in out)


def test_per_user_namespace_isolation(tmp_path) -> None:
    a = MentatSkillBank.for_user(tmp_path, user_id="alice")
    b = MentatSkillBank.for_user(tmp_path, user_id="bob")
    assert a.bank.active_dir != b.bank.active_dir


def test_erase_cascades_user_skills(tmp_path) -> None:
    bank = MentatSkillBank.for_user(tmp_path, user_id="alice")
    rec = SkillRecord(
        skill=Skill(name="alpha", description="d", prompt="body"),
        trust_tier=TrustTier.T2_AUTO_EXTRACTED,
    )
    bank.bank.add(rec)
    assert bank.bank.has(rec.skill.slug())
    deleted = bank.erase()
    assert deleted >= 1
    md = bank.bank.active_dir / rec.skill.slug() / "SKILL.md"
    assert not md.exists()
