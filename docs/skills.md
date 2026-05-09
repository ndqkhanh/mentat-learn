---
title: Mentat-Learn — Skills (full AutoSkill, multi-channel)
description: Direct AutoSkill instantiation. Per-user dialogue across Slack/WhatsApp/Telegram/email/iMessage/web; consent-gated; right-to-erasure.
---

# Mentat-Learn — Skills (full AutoSkill)

Mentat-Learn's architecture explicitly describes the Hermes-style closed
skill-learning loop. This integration realises that — full AutoSkill on
multi-channel dialogue with per-user consent gates and right-to-erasure.

## Corner of the design space

| Axis | Value |
|---|---|
| Feedback signal | LLM judge (P_judge), no ground truth |
| Skill artifact | Single SKILL.md per user × preference |
| Parameter access | Frozen weights |
| Reference paper | [AutoSkill](../../../docs/167-autoskill-experience-driven-lifelong-learning.md) — direct target |

## Adapter

`mentat_learn.skills_adapter` provides:

- `MentatDialogueExtractor` — wraps DialogueExtractor; reads channel-merged turns.
- `MentatUserSkillBank` — per-user namespace under
  `~/.mentat/skills/Users/<user_id>/`.
- `delete_user_skills(user_id)` — right-to-erasure helper.

## Bright-lines

- `BL-MENTAT-SKILL-CONSENT` — opt-in capture per user.
- `BL-MENTAT-SKILL-CROSS-CHANNEL` — channel metadata never leaks.
- `BL-MENTAT-SKILL-MULTI-USER-EXPORT` — no cross-user transfer.

## Seed skills

- `cross-channel-persona` — same persona across all channels.
- `user-style-preference` — captures per-user style.
