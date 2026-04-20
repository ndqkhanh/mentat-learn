# Mentat-Learn Block 10 — Self-Eval Every 15 Tasks

## Responsibility

Every 15 completed tasks, Mentat runs a self-evaluation pass: skill correctness, persona alignment, privacy compliance, dialectic stability. Retires low-performing skills, flags drift.

Reference: [docs/55 Hermes Agent](../../../docs/55-hermes-agent-self-improving.md) (self-eval cadence), [docs/21 LLM-as-Judge](../../../docs/21-llm-as-judge-trajectory-eval.md), [docs/11 verifier loops](../../../docs/11-verifier-evaluator-loops.md).

## Eval cadence

- Triggered by a task-completion counter. Default 15 tasks per cycle; user-configurable.
- Runs asynchronously (off critical path).
- Emits a structured report stored in a user-visible log.

## Checks per cycle

### 1. Skill correctness
- Sample recent uses of each skill (up to 5 per skill).
- Was the outcome aligned with the skill's declared description?
- Did the user edit / redo the output significantly?
- Compute a per-skill trend score.

**Action:** skills with declining success_rate flagged for retirement; composite skills with low utility un-composed (base skills restored to preferred).

### 2. Persona alignment
- Sample recent agent replies across channels.
- Prompt: "Does this reply match the persona described in SOUL.md? Any drift?"
- Compute persona-drift score.

**Action:** if drift > threshold, ask user to review SOUL.md.

### 3. Privacy compliance
- Sample recent turns.
- Check: any PII written to persistent memory without consent? Any cross-channel leakage?
- Check: memory reads respected consent flags?

**Action:** non-zero → incident logged; user notified.

### 4. Dialectic stability
- Compare current dialectic summary to summary from 15 tasks ago.
- Sharp changes without user-driven life-context changes indicate feedback loop.

**Action:** if unstable, the dialectic is paused for user review.

### 5. Cost and latency
- Per-cycle cost trend.
- p95 latency trend.

**Action:** regression > threshold triggers alerts.

## Report format

```markdown
# Self-eval report — cycle #27 (last 15 tasks)

## Skills
- weekly-review         : use_count=4, success_rate=0.95 → healthy
- morning-brief         : use_count=2, success_rate=0.50 → ⚠ flagged for review
- draft-response        : use_count=6, success_rate=0.92 → healthy

## Persona drift
- score=0.12 (low) → stable

## Privacy
- compliance checks: pass
- redaction events this cycle: 3

## Dialectic
- stability: high
- notable: "expertise level" remains unchanged

## Cost
- avg cost/turn: $0.04 (↓ from $0.05 last cycle — skill cache improving)
```

Stored at `~/.mentat/self-eval/cycle-N.md`; user-readable.

## User feedback loop

User can respond:
- Approve retirement of a flagged skill.
- Restore a disabled skill.
- Request deeper review of a specific skill or dimension.
- Reset dialectic.

Feedback is applied, then next cycle re-evaluates.

## Failure modes

| Mode | Defense |
|---|---|
| Self-eval costs too much | Budget per cycle; can be skipped on cost pressure |
| Self-eval judges its own judging | LLM judge is separate call with temperature 0; diversified model if available |
| Over-retiring skills | User approval gate on retirement |
| Eval missing drift | Complemented by in-turn indicators (user corrections, skill refinement signals) |
| Cycle timing coincides with high-stakes task | Eval runs async; never blocks user turns |

## Metrics

- `self_eval.cycles_run`
- `self_eval.skills_flagged`
- `self_eval.skills_retired`
- `self_eval.persona_drift_score`
- `self_eval.privacy_incidents` (should be zero)
- `self_eval.user_feedback_actions` (what user changed after seeing the report)
