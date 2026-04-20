# Mentat-Learn — Architecture Trade-offs

## Trade-off 1: Skill extractor always-on vs on-demand

**Chosen:** Always-on at end of every completed task; refinement on every reuse.

**Alternative:** On-demand — user explicitly says "remember how you did this".

**Why:** Hermes Agent's insight is that the bar is not "storing what happened" (everyone does that) but "storing what worked" (hardly anyone does). On-demand skill creation leaves most value on the table; users don't reliably volunteer.

**Cost:** Occasional low-value skills get written. Mitigated by compression pass ([block 04](blocks/04-skill-extractor-loop.md)) that prunes unused skills.

## Trade-off 2: Skill compression vs flat library

**Chosen:** Compress co-occurring skills into higher-order composites after repeated co-invocation.

**Alternative:** Flat library, grow forever.

**Why:** Skill libraries degrade in discoverability past ~100 skills. Compression keeps the discovery surface small while preserving the base skills. Directly inspired by [Voyager](../../docs/19-voyager-skill-libraries.md)'s library + practical observations from OpenClaw users.

**Cost:** Compression pass must be correct; bad composites can subsume valuable base skills. Mitigated by keeping the base skills callable even when marked "subsumed".

## Trade-off 3: Unified gateway vs channel-specific agents

**Chosen:** One gateway, one persona, all channels.

**Alternative:** Per-channel agents with per-channel personas.

**Why:** OpenClaw's multi-channel gateway is the dominant pattern because users actually want "the same agent on every channel". Mentat takes it further with SOUL.md-anchored persona for continuity.

**Cost:** Channel-specific behavior (WhatsApp emojis, Slack mentions) must be expressible as output adapters, not separate agents.

## Trade-off 4: Four-layer memory vs Hermes-style three-layer

**Chosen:** Procedural + facts + session + Honcho dialectic = 4 layers.

**Alternative:** Procedural + facts + session = 3 layers (Hermes's default).

**Why:** The Honcho dialectic layer is powerful specifically for personal agents (it models the *relationship* over time, not just facts). It's optional in Hermes; Mentat makes it standard. Personal assistants live or die by feeling personal.

**Cost:** More LLM calls to maintain the dialectic model. Small marginal cost.

## Trade-off 5: SOUL.md-anchored persona vs runtime prompt engineering

**Chosen:** Immutable SOUL.md partition in context; user editable but require conscious commit.

**Alternative:** Runtime-mutable persona (agent adapts on the fly).

**Why:** Persona drift is a real failure mode. SemaClaw's SOUL.md pattern is the cleanest control against drift. Mentat honors it.

**Cost:** Less "adaptive personality" on the fly. Users who want that can edit SOUL.md explicitly.

## Trade-off 6: Autogenesis-versioned skills vs plain Markdown

**Chosen:** Versioned patches with propose → evaluate → commit → rollback-on-regression.

**Alternative:** Plain Markdown files; edits are in-place.

**Why:** Skills evolve; bad edits happen. The Autogenesis protocol from [docs/36](../../docs/36-autogenesis-self-evolving-agents.md) gives us a rollback path and an evaluation gate without human-managed versioning overhead.

**Cost:** Slightly more infra. Low cost.

## Trade-off 7: NLAH slot for advanced users vs code-only harness

**Chosen:** Default harness is code; advanced users can supply `HARNESS.md` in Natural-Language Agent Harness form ([arXiv:2603.25723](https://arxiv.org/abs/2603.25723)).

**Alternative:** Pure code harness.

**Why:** NLAH lets power users express personal agent behavior ("if user mentions 'work emergency' on Sunday, never auto-reply on my behalf") without forking. The IHR (Intelligent Harness Runtime) executes the NL contract.

**Cost:** Requires shipping an IHR execution layer; must be carefully sandboxed.

## Trade-off 8: Self-eval every 15 tasks vs continuous

**Chosen:** Periodic self-eval every 15 tasks, same as Hermes.

**Alternative:** Continuous evaluation.

**Why:** Personal agents don't have a tight ground-truth loop. 15-task cadence amortizes eval cost; a compromise between catching drift early and not burning compute.

**Cost:** Drift may persist for up to 15 tasks before detection. Acceptable for a personal agent.

## Trade-off 9: Privacy scope per channel vs single opt-in

**Chosen:** Per-channel consent flags; per-scope memory gates.

**Alternative:** Single "I consent to memory" toggle.

**Why:** Users have different expectations per channel. Work Slack ≠ personal WhatsApp. Per-channel consent respects this and is technically trivial.

**Cost:** UX complexity for the consent dashboard. Worth it.

## Trade-off 10: Cache-aware skill loading vs always-loaded

**Chosen:** Skills are indexed + loaded just-in-time when their description matches.

**Alternative:** Always-loaded (small library only).

**Why:** If library grows past ~50 skills, always-loaded is a token bomb. Cache-aware loading is the mechanism Hermes used to scale library size without scaling token cost.

**Cost:** One extra embedding + match step per turn. Negligible.

## Rejected alternatives

- **Central cloud-managed skill repository with publisher rating.** Privacy dispreferred by target user base (personal assistants).
- **Training a personal fine-tune.** Cost-prohibitive per user; skill library gets ~80% of the value.
- **Voice-first pivot.** That's Harmony-Voice's niche. Mentat is text-plus-automations-first; voice is a channel.
- **Multi-user / team mode.** That's Syndicate's niche. Mentat is one-user-one-household.
