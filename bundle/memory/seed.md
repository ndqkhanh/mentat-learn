# Mentat-Learn seed memory

## Default channel adapters

- `slack` — Block Kit rendering, threaded replies.
- `whatsapp` — Plain-text + structured templates.
- `telegram` — Markdown V2 rendering, inline buttons.
- `email` — HTML + plain-text dual-render.

## Default memory tier params

- Episodic window: 200 turns / 7 days.
- Semantic dedup: cosine ≥ 0.92 → merge.
- Procedural promotion: `seen_count ≥ 3 ∧ confidence ≥ 0.85`
  (Lyra v3.11 L311-8).
- Dialectic update: weekly batch via Lyra v3.7 routine.

## Default redaction patterns

The redactor ships with the standard PII pattern set
(email / phone / cc / API key) plus the user-supplied allow-list
in `~/.mentat-learn/redactor/allowlist.txt`.
