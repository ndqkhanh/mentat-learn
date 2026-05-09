# Mentat-Learn Block 03 — Four-Layer Memory

## Responsibility

Mentat's memory is composed of four distinct layers, each with its own TTL policy, update rules, and role in the turn. The four-way split extends Hermes Agent's three-layer design ([docs/55](../../../docs/55-hermes-agent-self-improving.md)) with an explicit dialectic layer.

## The four layers

### 1. Procedural (the skill library)

Reusable procedures the agent can invoke. Covered by [block 05 Skill Library](05-skill-library.md). Written by [block 04 Skill Extractor Loop](04-skill-extractor-loop.md).

TTL: effectively infinite, but subject to compression + pruning.

### 2. Facts / Preferences

Structured memory of user-specific facts: preferences (style, times, formats), relationships ("my sister is Amy"), standing tasks ("always CC Bob on engineering emails"), and durable context ("I'm a backend engineer; don't over-explain Python").

- FTS5 full-text index for keyword recall.
- Embedding index for semantic recall.
- Written by the extractor on explicit user statements (not implicit inference unless consented).

TTL: until user forgets them or they're superseded.

### 3. Session Working Context

Per-session turn history, truncated with [docs/08 context-compaction](../../../docs/08-context-compaction.md) techniques once size exceeds a threshold.

TTL: session lifetime + a short grace window; purged on explicit "forget this conversation".

### 4. Dialectic (Honcho)

Models the relationship between user and agent across ~12 identity dimensions (communication style, expertise level, trust level, topic affinities, etc.). Updated incrementally on each turn.

See [block 09 Dialectic User Modeling](09-dialectic-user-modeling.md) for details.

## Memory read flow

Each turn:

1. Session layer: last N turns inlined verbatim.
2. Facts: top-K via hybrid retrieval (FTS5 + embedding) against the user turn.
3. Procedural: delegated to [skill match ranking](02-agent-loop.md).
4. Dialectic: short summary of relationship state appended as a system-prompt addendum.

Total memory footprint budgeted to ~8 % of the LLM's context window by default.

## Memory write flow

- Facts: written explicitly from extractor output when a statement like "I prefer X" is detected; confidence tagged.
- Procedural: see [block 04](04-skill-extractor-loop.md).
- Session: every turn.
- Dialectic: delta update every turn.

## Provenance + consent

Every memory entry carries:
- `source_channel` (where it came from).
- `timestamp`.
- `consent_level` ("session-only", "persist-personal", "persist-shared-across-channels").

Retrieval honors consent: a fact tagged session-only never surfaces outside its session.

## TTL policies per layer

| Layer | Default TTL | Refresh on use |
|---|---|---|
| Procedural | infinite | Yes (bumps use_count) |
| Facts | 180 days or user-set | Yes |
| Session | session + 24 h | No |
| Dialectic | rolling (no deletion) | continuous update |

## Failure modes

| Mode | Defense |
|---|---|
| Memory bloat | Per-layer size caps + compaction |
| Incorrect fact persists | User can delete via `/v1/me/memory/{id}` |
| Cross-session leakage of session-only | Strict consent-level filter on retrieval |
| Dialectic drift (model feedback loop) | Periodic self-eval ([block 10](10-self-eval.md)) |
| PII in facts | Pre-ingest redactor honoring user's PII scrubbing preference |

## Metrics

- `memory.reads_per_turn` by layer
- `memory.writes_per_turn` by layer
- `memory.size_bytes` per user + layer
- `memory.consent_rejections` (surface-high — indicates over-eager extraction)
- `memory.deletion_events`
