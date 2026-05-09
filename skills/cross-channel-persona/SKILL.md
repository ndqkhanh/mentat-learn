---
name: 'cross-channel-persona'
description: 'Aggregate per-user persona across Slack / WhatsApp / Telegram / email / iMessage / web without leaking which channel a fact came from.'
version: '0.1.0'
triggers: ['persona', 'channel', 'soul']
tags: ['preference', 'cross-channel', 'consent']
---

# Goal
Maintain a single persona per user, anchored on `SOUL.md`, that pulls
signal from every authorised channel and never leaks one channel's
existence to another.

# Constraints & Style
- `SOUL.md` is the anchor; per-skill is per-user, not per-channel.
- Channel name and channel-specific identifiers (Slack ID, phone, email
  domain) must be stripped from skill bodies before merge.
- Channel attribution lives only in `provenance.jsonl`, never in the
  rendered skill content.
- Bright-line: `BL-MENTAT-SKILL-CROSS-CHANNEL` — a skill extracted from
  channel A cannot reveal channel A's existence when used in channel B.

# Workflow
1. Receive a candidate skill from an extractor; capture
   `channel_id` only in provenance.
2. Run the channel-leak gate: regex over the skill body for known
   channel tokens (`@slack`, `+phone`, `iMessage`, etc.); reject on hit.
3. Merge into the user's `Users/<user_id>/` namespace via
   `SkillBank.merge`; bump patch version.
4. On a deletion request for the user, cascade delete every skill in
   `Users/<user_id>/` and append a tombstone to `provenance.jsonl`.
