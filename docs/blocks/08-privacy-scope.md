# Mentat-Learn Block 08 — Privacy Scope

## Responsibility

Memory is opt-in. Consent flags are per channel. Users can say "forget that" at any time. PII scrubbers run on relevant egress paths. No cross-user data movement.

References: [docs/22 guardrails](../../../docs/22-guardrails-prompt-injection.md), [docs/41 product-control-plane](../../../docs/41-product-control-plane.md).

## Consent model

Per-channel consent flags:

```yaml
channel: slack
  persistent_memory: true         # allow memory across sessions
  cross_channel_share: false      # don't share with WhatsApp etc.
  scheduled_automations: true
  attachments_may_enter_memory: false

channel: whatsapp
  persistent_memory: true
  cross_channel_share: true
  ...
```

Default is the safest: memory = off, cross-channel = off. User enables explicitly.

## "Forget that" semantics

Three purge levels:

1. **Forget this message** — remove from session only.
2. **Forget this thread** — purge the session and any memory entries that cite it.
3. **Forget everything** — purge all user memory (facts, procedural, session, dialectic) except for skills the user explicitly marked "keep".

All purge operations are irreversible (tombstone entry added to the audit log showing purge time, but purged content is gone).

## PII scrubbing

Scrubber patterns (extensible):
- Email addresses, phone numbers, credit card shape.
- Named-entity recognition for names (user can opt-out — sometimes memory *wants* names).
- Session-specific credentials (if user pastes an API key, it's redacted before entering memory).

Scrubber runs on:
- Egress to memory (pre-write).
- Egress to exported skills (pre-share).
- Egress to Honcho's dialectic model (if user opts in to dialectic with PII-scrub on).

## Cross-user isolation

- Per-user storage directories; per-user Redis keyspace; per-user credential encryption keys.
- No shared memory across users. Period.
- Community-shared skills are anonymized at export; personal identifiers stripped.

## Audit of memory access

- Every read from persistent memory is logged in a lightweight access log.
- User can request an access report showing what memory was read when by which turn.
- Retention of access log: 90 days by default, user-configurable.

## Regulatory posture

- GDPR: lawful basis = consent; right to erasure via "forget everything".
- HIPAA (if agent is used in healthcare context, not recommended): additional BAA required.
- PCI: credit card shape stripped at ingest; never enters memory.
- CCPA: "forget" flow satisfies "right to delete".

## Failure modes

| Mode | Defense |
|---|---|
| Consent state change not propagated | Cache invalidation on consent update |
| PII scrubber misses a pattern | User-extensible rules; CI test on known PII shapes |
| Forget request during active turn | Queue for end-of-turn to avoid breaking in-flight reasoning |
| Session memory leak to shared skill export | Pre-export redactor with CI verifiers |

## Metrics

- `privacy.consent_updates`
- `privacy.forget_events` by scope
- `privacy.pii_redactions` per channel
- `privacy.access_log_reads`
- `privacy.noncompliance_events` (should be zero)
