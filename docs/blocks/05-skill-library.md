# Mentat-Learn Block 05 — Skill Library

## Responsibility

Persistent, cache-aware, versioned library of skills. agentskills.io-compatible SKILL.md format. Loaded on demand; token bill doesn't scale with library size.

References: [docs/04 Skills](../../../docs/04-skills.md), [docs/19 Voyager](../../../docs/19-voyager-skill-libraries.md), [docs/55 Hermes](../../../docs/55-hermes-agent-self-improving.md).

## Storage

- Per-user directory on disk: `~/.mentat/skills/<name>.md`.
- Version history in sibling `~/.mentat/skills/<name>/versions/` (copy-on-write).
- Embedding index for description matching (local vector store; no cloud dependency).

## Schema (frontmatter)

```yaml
---
name: string (unique per user)
description: string (routing hint; one-line; 50–120 chars)
version: int
required_tools: [tool-name]
tags: [string]
subsumed_by: UUID | null
use_count: int
success_rate: float | null
last_updated: iso-datetime
source: "extracted" | "imported" | "user-authored"
---
```

Body is free-form Markdown with a `# Steps` section (required) and optional `# Learnings`, `# Examples`, `# Preconditions`.

## Loading model (cache-aware)

- On Mentat startup: load the *index* only — name, description, tags, required_tools, stats.
- On skill invocation: load the body JIT.
- Bodies cached in-process with LRU (default cap: 50 active bodies).
- Anthropic prompt caching on the stable system prompt keeps the token-stream cost flat as the library grows.

## Routing

Agent loop's skill-match step queries the library via:

1. Embedding similarity over descriptions.
2. Tag match (boost if tag matches any active-session label).
3. Stat multiplier (success_rate + log(use_count)).

See [block 02 Agent Loop](02-agent-loop.md) for the scoring formula.

## User controls

- `GET /v1/skills` — list all skills.
- `POST /v1/skills/{id}/disable` — opt out without deleting.
- `DELETE /v1/skills/{id}` — permanent removal + version history purge (consent-gated).
- `POST /v1/skills/{id}/promote` — force-prefer this skill (bypasses matcher scoring).

## Import / export

- Export: user can export their entire skill library as a tarball.
- Import: compatible SKILL.md files (from agentskills.io or another Mentat user) imported with "source=imported"; initial stats zeroed.
- Privacy: exported skills go through a PII redactor to strip user-specific identifiers before sharing.

## Federation (opt-in, post-v1)

Users can contribute anonymized templates (PII stripped, names replaced with placeholders) to a shared community library. Others can import with one-click. First application of [docs/47 Adaptation Survey T2](../../../docs/47-adaptation-of-agentic-ai-survey.md) as community infrastructure.

## Failure modes

| Mode | Defense |
|---|---|
| Library corruption | Per-skill separate files; corruption isolated |
| Embedding drift across model upgrades | Re-embed on upgrade; version the embedding model |
| Skill with missing `required_tools` | Skill matcher excludes skills whose tools aren't available |
| Importing poisoned skills | Import through eval gate; run on held-out synthetic turns; commit on pass |

## Metrics

- `skill_library.size` per user
- `skill_library.cache_hit_rate`
- `skill_library.avg_use_per_skill`
- `skill_library.disabled_count`
- `skill_library.federation_imports` (if enabled)
