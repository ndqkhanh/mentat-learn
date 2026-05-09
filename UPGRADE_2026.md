# Mentat-Learn — May-2026 Upgrade Stub

> Companion to [`../CROSS_PROJECT_UPGRADE_PLAN_2026.md`](../CROSS_PROJECT_UPGRADE_PLAN_2026.md).
> Per the cross-project matrix, Mentat-Learn is **W4** — design-only;
> a walking-skeleton must land before the bundle plan applies.

## Headline gap (vs 2026 SOTA)

- **No code** — Mentat-Learn is design-only as of v0.1 (April 2026).
- **No `bundle/`** — depends on the walking-skeleton landing first.
- **Self-improvement loop** — the four-layer memory + skill extractor
  + Honcho user model design is on paper; once implemented, it should
  align with Lyra v3.9 Recursive Curator ([`L39-3 self-curation`](../lyra/LYRA_V3_9_RECURSIVE_CURATOR_PLAN.md))
  so the two systems share invariants instead of duplicating them.

## Smallest upgrade in this pass

A **template `bundle/` skeleton** — directory layout + manifest
placeholder, no live code. Lets Mentat-Learn ship its walking-skeleton
straight into the v3.11 ecosystem when ready.

```text
mentat-learn/bundle/   # template only
├── bundle.yaml.template
├── persona.md.template
├── skills/.gitkeep
├── tools/.gitkeep
├── memory/.gitkeep
├── evals/.gitkeep
└── verifier/.gitkeep
```

## Walking-skeleton order (out of scope here)

1. Implement the four-layer memory store.
2. Implement the skill extractor on top of Lyra v3.7 auto-memory.
3. Implement Honcho user model adapter.
4. Wire to Slack / WhatsApp / Telegram / email connectors as MCP servers.
5. *Then* apply this upgrade plan.

## Sequencing

W4 — long-tail; depends on every other upgrade landing first plus
the project's own walking-skeleton.

## Related Lyra phases

- L37-6 Auto-memory — the durable substrate Mentat-Learn extends.
- L39-3 Self-curation — invariant alignment when Mentat-Learn ships.
- L311-4 SourceBundle — the contract for eventual install.
