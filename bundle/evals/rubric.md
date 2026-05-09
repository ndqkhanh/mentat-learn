# Mentat-Learn eval rubric

A trace **passes** when:

1. Channel envelopes match the canonical schema regardless of
   source channel.
2. Redaction strips every PII pattern before memory write
   (`LBL-MENTAT-PRIVACY`).
3. Cross-user memory reads blocked (`LBL-MENTAT-USER-ATTR`).
4. Skill promotion fires only when both thresholds are met
   (`seen_count ≥ 3 ∧ confidence ≥ 0.85`).
5. Demotion fires when both demotion thresholds are met
   (`confidence < 0.30 ∧ age_days > 7`).

Aggregate metrics:

- **Channel-neutrality** — fraction of envelopes matching the
  canonical schema (target 1.0).
- **PII redaction rate** — fraction of PII-containing messages
  redacted before memory write (target 1.0).
- **User-attribution compliance** — fraction of cross-user attempts
  blocked (target 1.0).
- **Promotion accuracy** — fraction of would-be promotions that
  fired correctly (target ≥0.95).
- **Demotion accuracy** — fraction of demotions firing on the
  expected day (target ≥0.95).
