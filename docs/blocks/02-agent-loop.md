# Mentat-Learn Block 02 — Agent Loop

## Responsibility

Core reasoning loop for a single user turn. Skill-retrieval first; first-principles fallback; always produces a trace the skill extractor can consume.

Reference: [docs/01 agent-loop-architecture](../../../docs/01-agent-loop-architecture.md).

## Turn flow

1. **Assemble context** — SOUL.md, last N turns of the session, top-K memory entries (procedural + facts), Honcho user-model summary.
2. **Skill match** — embed the user turn; compare against skill descriptions in the library; return top-K candidates above similarity threshold.
3. **Skill invocation (if matched)** — load the skill's body_md into context; narrow the tool allowlist to the skill's `required_tools`; execute.
4. **First-principles fallback (if no match)** — classic agent loop: tools → observations → synthesis.
5. **Stop conditions** — model emits end-of-turn / max steps / cost cap.
6. **Task-end detection** — heuristic + explicit markers signal the skill extractor to consider this trace.

## Skill match ranking

Each skill carries a `description` (one-line), tags, `required_tools`, and a `use_count` + `success_rate` stat. Match scoring:

```
score = 0.6 * embedding_sim(turn, description)
      + 0.2 * success_rate
      + 0.2 * log(1 + use_count) / log(50)
```

Above threshold → use skill. Tie-break: most recently updated wins.

## Re-anchoring against drift

Every N steps (default 8), the loop re-injects:
- SOUL.md snippet.
- Current todo (if any).
- Most recent tool output summary.

Directly addresses [HORIZON's](../../../docs/27-horizon-long-horizon-degradation.md) context-forget failure class on multi-step personal tasks.

## ReBalance confidence steering

For multi-skill compositions, confidence signals drive depth:
- High-variance token stream → steer deeper ([ReBalance](../../../docs/51-rebalance-efficient-reasoning.md)).
- Consistent high confidence on easy lookups → skip extra iterations.

## Budget

- Default per-turn step budget: 20.
- Default per-turn cost cap: $0.20 on cache-hit-skill path; $0.60 on first-principles.
- Per-day per-user cost cap: $5 (user-configurable).

## Failure modes

| Mode | Defense |
|---|---|
| Skill-match false positive (wrong skill loaded) | Success-rate decays on failure; user can disable a skill; extractor can retire it |
| Infinite skill recursion | Skills cannot invoke themselves; depth cap 2 |
| Budget exhaustion mid-turn | Graceful truncation with "I hit my budget; here's what I have" |
| Persona drift during long sessions | SOUL.md re-anchor every N steps |

## Metrics

- `loop.skill_match_rate`
- `loop.skill_success_rate` (per skill)
- `loop.first_principles_rate`
- `loop.avg_steps_per_turn`
- `loop.rebalance_depth_distribution`
- `loop.reanchor_events`
