---
name: skill-extractor
description: Closed-loop skill extraction — repeated patterns become durable skills.
---
# Skill Extractor

The closed loop:

1. Every interaction logs to episodic memory.
2. The extractor periodically scans for repeated patterns —
   same intent + same resolution path.
3. When a pattern's `seen_count ≥ 3 ∧ confidence ≥ 0.85`
   (Lyra v3.11 L311-8 thresholds), the pattern auto-promotes to a
   procedural-memory skill.
4. The new skill is named, documented, and added to the agent's
   active skill set automatically.

Demoted patterns (`confidence < 0.30 ∧ age_days > 7`) tombstone
back to the episodic tier.

This is the "Mentat learns" half of the name — the agent gets
better at *this user* over time without explicit prompting from
the user.
