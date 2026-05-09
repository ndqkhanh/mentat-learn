# Mentat-Learn Block 09 — Dialectic User Modeling (Honcho)

## Responsibility

Maintain a small, evolving model of the **relationship** between the user and the agent across ~12 identity dimensions. Updated every turn; consulted on persona-alignment decisions. The dialectic is explicit: it models both what the user is like *and* what the agent is for them.

Reference: [docs/55 Hermes Agent](../../../docs/55-hermes-agent-self-improving.md) — Honcho dialectic user modeling.

## Why dialectic, not just facts

A fact: "user is a backend engineer".
A dialectic entry: "user treats agent as a *peer technical reviewer*, not as an assistant — they push back on suggestions; respond to short, evidence-backed replies; dislike when agent over-explains".

Facts don't capture the second kind. Personal agents that only hold facts feel flat; agents that hold the dialectic feel coherent.

## The ~12 dimensions

Approximate — tuning per deployment. Each is a short slot the agent maintains:

1. **Expertise level** (novice / intermediate / expert / mixed across domains)
2. **Communication preference** (terse / medium / expansive)
3. **Detail tolerance** (over-explain is fine / never over-explain)
4. **Trust level** (earn trust each time / trusted by default / actively skeptical)
5. **Topic affinity** (what they actually want to talk about)
6. **Topic aversion** (what they want the agent to shut up about)
7. **Authority posture** (agent is assistant / peer / external resource / tool)
8. **Humor tolerance** (dry humor OK / strictly formal / playful)
9. **Error response** (apologize / fix and move on / explain why)
10. **Pacing** (respond fast / respond when ready)
11. **Channel preferences** (Slack for work, WhatsApp for personal, etc.)
12. **Current life context** (work-stress / traveling / family-event / normal)

## Update rules

Each turn:
- LLM pass with the turn + current dialectic summary → proposed diffs.
- Diff is applied only if confidence ≥ threshold.
- Dialectic history retained (rolling window of ~100 turns for reconstruction if needed).

## Consultation

The dialectic summary is appended (briefly) to the system prompt. The agent loop consults it for:

- Tone calibration ("terse vs expansive" shapes reply length).
- Topic routing ("user averse to crypto talk" → skip suggested optional aside).
- Error-response style.
- Over-explain avoidance.

## Divergence detection

If dialectic drifts sharply over a short window (e.g., user's "expertise" suddenly drops from expert to novice — might be a guest using the account), Mentat asks: "quick check — is this still you, or am I talking with a guest?"

## Consent and privacy

Dialectic is the most sensitive layer because it's a model of the user themselves. Opt-in only; off by default. Can be disabled without deleting other memory. Purge semantics identical to other layers: "forget the dialectic" returns the agent to stock posture.

## Failure modes

| Mode | Defense |
|---|---|
| Model feedback loop (agent shapes user to match its model) | Self-eval every 15 tasks flags suspicious stability |
| Off-by-one drift on key dimensions | Rolling window retained; user can reset specific dimensions |
| Privacy violation (revealing dialectic guess to 3rd party) | Dialectic never sent outside the agent's own prompt |
| Guest-account confusion | Divergence-detection prompt |
| Dialectic bloat | Hard caps on per-dimension tokens |

## Metrics

- `dialectic.updates_per_turn` (should settle to a steady rate)
- `dialectic.divergence_events`
- `dialectic.user_overrides` (user correcting agent's guess)
- `dialectic.disable_rate` (if high, product signal)
