---
name: four-layer-memory
description: Episodic / semantic / procedural / dialectic memory tiers.
---
# Four-Layer Memory

The four tiers, in increasing abstraction:

1. **Episodic** — raw turn log; sliding window, fast write.
2. **Semantic** — distilled facts ("user is vegan", "user lives in
   Berlin"); deduplicated, contradiction-checked.
3. **Procedural** — repeated patterns promoted from auto-memory
   (Lyra v3.11 L311-8) when `seen_count ≥ 3 ∧ confidence ≥ 0.85`.
4. **Dialectic** — Honcho-style user model: preferences,
   communication style, decision patterns. Queryable.

Reads cascade from procedural → dialectic → semantic → episodic;
writes land in episodic and bubble up through promotion gates.

`LBL-MENTAT-USER-ATTR`: every entry across every tier carries a
user-identity binding. Cross-user reads are blocked at the
substrate.
