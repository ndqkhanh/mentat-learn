# Mentat-Learn — Architecture

## What Mentat-Learn is

Mentat-Learn is a **self-improving personal assistant**: one coherent persona the user meets across multiple channels (Slack, WhatsApp, Telegram, email, iMessage, web), which *actually gets more capable over time* — not by updating its configuration, but by extracting reusable procedures from completed workflows and composing them into a growing skill library. It fuses the best pieces of [OpenClaw](../../docs/52-dive-into-open-claw.md) (multi-channel gateway), [SemaClaw](../../docs/54-semaclaw-general-purpose-agent.md) (DAG teams + SOUL.md persona + PermissionBridge), and [Hermes Agent](../../docs/55-hermes-agent-self-improving.md) (closed skill-learning loop + Honcho dialectic user model).

This is the personal-agent analogue of [Orion-Code](../orion-code/architecture.md) for coding, but its optimization target is not task success — it's **cross-session capability growth**.

## Honest baselines

| Baseline | Reported number / shape |
|---|---|
| **OpenClaw** (~196k stars Apr 2026) | Multi-channel agent, SKILL.md invocable capabilities, but no auto-skill-extraction across sessions ([docs/52](../../docs/52-dive-into-open-claw.md)) |
| **Hermes Agent** (Nous Research) | Closed learning loop: completed task → pattern extraction → Markdown SKILL.md → refined on next use; self-eval every 15 tasks ([docs/55](../../docs/55-hermes-agent-self-improving.md)) |
| **SemaClaw** (Midea AIRC, arXiv:2604.11548) | DAG-based two-phase hybrid orchestration; PermissionBridge runtime checkpoints; SOUL.md persona partition; agentic wiki ([docs/54](../../docs/54-semaclaw-general-purpose-agent.md)) |
| **Voyager** (Minecraft) | Skill library with curriculum + code-based verification; transfers across worlds ([docs/19](../../docs/19-voyager-skill-libraries.md)) |
| Generic LLM chatbot | No memory across sessions; no skill accumulation; no persona continuity |

## Design targets (hypotheses)

- **Measurable cross-session productivity gain.** Mean steps / token cost for a given workflow class drops ≥ 30 % from turn N to turn N+20. **Assumption:** skill extractor reliably captures repeatable procedures; cache-aware skill loading keeps the context cost flat.
- **Persona fidelity.** User-surveyed "agent felt consistent" score ≥ 0.9 across ≥ 5 interactions. **Assumption:** SOUL.md-anchored persona partition ([docs/54](../../docs/54-semaclaw-general-purpose-agent.md)) plus Honcho dialectic modeling ([docs/55](../../docs/55-hermes-agent-self-improving.md)) anchor identity.
- **Zero privacy regression.** Per-channel consent flags respected; opt-in memory is deletable; no cross-tenant data movement.
- **Gateway availability.** p95 latency end-of-message → first-reply < 1.2 s on cache-hit path.

## Component diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                           Mentat-Learn                                 │
│                                                                        │
│  Slack / iMessage / WhatsApp / Telegram / Email / Web   ◄── channels   │
│                            │                                           │
│                            ▼                                           │
│                    [Unified Gateway]                                   │
│                 (channel-agnostic routing)                             │
│                            │                                           │
│                            ▼                                           │
│                      [Agent Loop]                                      │
│                            │                                           │
│       ┌────────────────────┼─────────────────────┐                     │
│       ▼                    ▼                     ▼                     │
│  [Skill Library]   [Four-Layer Memory]     [Tool Layer + MCP]          │
│   (growing)                │                                           │
│                    procedural · facts                                  │
│                    session     · dialectic                             │
│       │                    │                     │                     │
│       └─────────┬──────────┴─────────────────────┘                     │
│                 ▼                                                      │
│         [Skill Extractor Loop]                                         │
│         (task complete → pattern → new SKILL.md)                       │
│                                                                        │
│   ↕ Cron-scheduled automations   ↕ Session persistence                 │
│   ↕ Privacy scope (per-channel)  ↕ Self-eval every 15 tasks            │
│   ↕ SOUL.md persona partition    ↕ Autogenesis-versioned artifacts     │
└────────────────────────────────────────────────────────────────────────┘
```

## The ten architectural commitments

1. **Unified Gateway** — single process routes messages across Slack, iMessage, WhatsApp, Telegram, Signal, email, and a web UI; one persona, one conversation context. See [blocks/01-gateway.md](blocks/01-gateway.md).
2. **Agent Loop with skill-retrieval** — harness loop invoking skills from the library by description match before falling back to first-principles reasoning. See [blocks/02-agent-loop.md](blocks/02-agent-loop.md).
3. **Four-Layer Memory** — procedural (skills), facts/preferences, session working context, Honcho-style dialectic model of user ↔ agent. See [blocks/03-four-layer-memory.md](blocks/03-four-layer-memory.md).
4. **Skill Extractor Loop** — after task completion, a pattern-miner writes a new SKILL.md; subsequent uses refine it; periodic compression merges co-occurring skills into composites. See [blocks/04-skill-extractor-loop.md](blocks/04-skill-extractor-loop.md).
5. **Skill Library** — cache-aware, agentskills.io-compatible, versioned via Autogenesis-style patches. See [blocks/05-skill-library.md](blocks/05-skill-library.md).
6. **Cron Scheduler** — user can say "every Monday at 9 draft my weekly review"; the scheduler becomes a first-class invocation path. See [blocks/06-cron-scheduler.md](blocks/06-cron-scheduler.md).
7. **Session Persistence** — conversations survive restarts, channel switches, device changes. See [blocks/07-session-persistence.md](blocks/07-session-persistence.md).
8. **Privacy Scope** — per-channel consent flags; opt-in cross-channel memory; PII scrubber on egress; immediate "forget that" semantics. See [blocks/08-privacy-scope.md](blocks/08-privacy-scope.md).
9. **Dialectic User Modeling (Honcho)** — agent models user and itself across ~12 identity dimensions; updated every interaction; optionally consulted for persona alignment. See [blocks/09-dialectic-user-modeling.md](blocks/09-dialectic-user-modeling.md).
10. **Self-Eval Every 15 Tasks** — periodic check on skill correctness + persona drift + privacy compliance; triggers skill pruning / retraining. See [blocks/10-self-eval.md](blocks/10-self-eval.md).

## Novel contributions (not present in cited systems)

1. **Skill compression** — co-occurring skills that the extractor detects being invoked together N times get merged into a higher-order composite; the base skills are kept but marked "subsumed" (callable but not preferred). New idea building on [Voyager](../../docs/19-voyager-skill-libraries.md)'s skill library + [Adaptation Survey T2](../../docs/47-adaptation-of-agentic-ai-survey.md)'s agent-supervised tool-side paradigm.

2. **Three-way composition of personal-agent patterns** — SOUL.md-anchored persona partition (SemaClaw) + Hermes's skill extractor + Honcho dialectic user modeling. Each of the three was novel alone; the three-way fusion is genuinely new. SOUL.md constrains *who the agent is*; Honcho models *who the user is to the agent*; the skill extractor grows *what the agent can do*. Together: coherent persona × deep user understanding × growing capability.

3. **Cache-aware skill loading** — skill bodies inlined just-in-time so the token bill doesn't scale with library size. The [Hermes Agent](../../docs/55-hermes-agent-self-improving.md) pattern, explicitly.

4. **Autogenesis-versioned skill artifacts** — each skill (and SOUL.md) is a versioned resource patch in the [Autogenesis protocol](../../docs/36-autogenesis-self-evolving-agents.md) sense: propose → evaluate → commit → rollback-on-regression. First application to a personal agent.

5. **Natural-Language Agent Harness slot (NLAH)** — advanced users can edit a natural-language harness spec (`HARNESS.md`) that is executed by an Intelligent Harness Runtime per [arXiv:2603.25723](https://arxiv.org/abs/2603.25723). Allows per-user personalized harness behavior without forking code.

## Non-goals

- Not a workplace chatbot; Mentat is bound to a single user / household unit.
- Not an enterprise orchestrator (that's Syndicate).
- Not a voice-first product (Harmony-Voice does that).
- Not an ops agent (Aegis-Ops is for that).

## Cross-references

- Trade-offs: [architecture-tradeoff.md](architecture-tradeoff.md)
- Operations: [system-design.md](system-design.md)
- Research: [docs/19](../../docs/19-voyager-skill-libraries.md), [docs/36](../../docs/36-autogenesis-self-evolving-agents.md), [docs/47](../../docs/47-adaptation-of-agentic-ai-survey.md), [docs/52](../../docs/52-dive-into-open-claw.md), [docs/54](../../docs/54-semaclaw-general-purpose-agent.md), [docs/55](../../docs/55-hermes-agent-self-improving.md).

## Status

Design specification, April 2026. Scaffold-quality. Not implemented. Target environment: self-hosted on a cheap VPS or serverless; deployable within the Nebius Token Factory stack or equivalent.
