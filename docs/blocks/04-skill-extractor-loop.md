# Mentat-Learn Block 04 — Skill Extractor Loop

## Responsibility

On every completed task, analyze the trace and decide whether a reusable procedure emerged. If yes, draft a `SKILL.md` in the agentskills.io format; evaluate it against similar past traces; commit on pass.

Reference: [docs/55 Hermes Agent](../../../docs/55-hermes-agent-self-improving.md) (closed learning loop, pattern extraction), [docs/19 Voyager](../../../docs/19-voyager-skill-libraries.md) (skill library), [docs/47 Adaptation Survey T2](../../../docs/47-adaptation-of-agentic-ai-survey.md) (agent-supervised tool-side).

## Extraction trigger

Triggered by:
- Explicit task end marker (model emits "done" or user acknowledges completion).
- N-turn idle after last tool action.
- User saying "remember how to do that" (explicit path).

## Extractor pipeline

1. **Input** — session summary + tool call sequence + task outcome (success / partial / failure).
2. **Is there a reusable pattern?** — LLM pass asking: "Is this procedure likely to recur?" If not, skip.
3. **Draft SKILL.md** — extract name, description, required_tools, numbered steps, key decision points.
4. **Retrieve comparable traces** — from memory (`FTS5` + embedding).
5. **Evaluate draft** — does the skill reproduce on comparable traces? LLM pass returns `pass` / `fail` / `partial`.
6. **Compress check** — does this skill's signature match an existing skill? (see "Skill Compression" below)
7. **Commit** — if pass: store as version 1, `use_count=0`, `success_rate=null`.

Failed drafts are not committed; but the attempt is logged for debugging the extractor itself.

## SKILL.md shape

```markdown
---
name: weekly-review
description: Draft the user's Friday weekly review from calendar + completed tasks
version: 3
required_tools: [calendar.read, notes.search, drafting.compose]
last_refined_at: 2026-04-20T17:10:00Z
use_count: 17
success_rate: 0.94
---
# Steps
1. Fetch calendar events from Mon–Fri of this week.
2. Cluster events by project / theme.
3. Pull any tasks marked "done" in this week.
4. Draft a 5-bullet summary: wins, blockers, next week.
5. Present to user for edit before sending.

# Learnings
- Skip meetings tagged "social"; user doesn't want them in the review.
- If calendar is empty, ask user if they were traveling.
```

## Skill Compression (novel)

When the extractor detects that skills A, B, C are invoked together ≥ N times (default 5) within single turns:

1. Draft a composite skill D that invokes A → B → C in sequence with shared context.
2. Evaluate D on held-out traces.
3. Commit D as `version 1`.
4. Mark A, B, C as `subsumed_by = D.id` (still callable, but the matcher prefers D).

Builds on [Voyager](../../../docs/19-voyager-skill-libraries.md)'s skill library idea with a novel compression operator that keeps the base skills available for re-use in other contexts.

## Refinement pipeline (per reuse)

When an existing skill is reused:

1. Execute skill.
2. If outcome differs from prior runs (new tool call added, different branch), LLM pass drafts a refined version.
3. Evaluate refined version; commit as `version N+1` on pass.

## Versioning + rollback (Autogenesis-style)

Each skill revision is a patch. On observed regression (success_rate drops sharply over recent window), the skill can be rolled back to the prior version. See [docs/36 Autogenesis](../../../docs/36-autogenesis-self-evolving-agents.md).

## Failure modes

| Mode | Defense |
|---|---|
| Skill garbage (not actually reusable) | Eval gate before commit; self-eval every 15 tasks retires low-success skills |
| Compression subsumes useful base skills | Base skills remain callable; compression is preference, not replacement |
| Extractor over-extracts trivial procedures | "Is this likely to recur?" gate filters one-off tasks |
| PII leakage into SKILL.md | Pre-commit redactor scrubs user-specific identifiers |
| Skill name collisions | Namespace per user; collision detection renames new skill |

## Metrics

- `extractor.drafts_per_day`
- `extractor.commit_rate`
- `extractor.compression_events`
- `skill.avg_success_rate` (fleet)
- `skill.retire_rate`
- `skill.rollback_events`
