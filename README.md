# Mentat-Learn — self-improving personal assistant (MVP)

Walking-skeleton implementation of the [Mentat-Learn design](architecture.md). A long-running assistant that learns from past sessions: builds a skill library, persists memory with provenance, runs self-evals, and carries skills forward to make later turns faster + cheaper.

## What works today

- **Session loop** — `/v1/turn` accepts user text and runs the dialectic + self-eval loop.
- **Skill library** — skills get acquired/refreshed across sessions; `/v1/skills` lists them with confidence + use counts.
- **Memory with provenance** — every memory item links back to the session that produced it; supports targeted forget patterns.
- **Privacy mode** — local-only by default; opt-in third-party provider via env vars.
- **Self-evals** — `/v1/self-eval` scores recent runs against rubrics and feeds results back into the skill confidences.
- **Cron / scheduler** — long-lived background tasks via the cron module.

## What is stubbed (honest MVP labels)

- LLM provider integration is `MockLLM` by default; switch to Anthropic via `ANTHROPIC_API_KEY`.
- Cross-machine sync is out of MVP scope.
- The dialectic / self-research loop is intentionally simple; v0.2 deepens it.

See [`architecture.md`](architecture.md) for the complete design.

## Run locally

```bash
make install        # creates .venv, installs harness_core + harness-tui + this project
make test           # run pytest
make run            # http://localhost:8008/docs
```

## TUI

A polished terminal interface ships out of the box, powered by the shared
[`harness-tui`](../../packages/harness-tui) package.

```bash
make install     # installs harness-tui editable alongside this project
make tui         # opens the TUI against the running FastAPI backend
make tui-mock    # demo: scripted events, no backend needed
```

Features:

- **Brand theme** with project ASCII logo + spinner pack.
- **Hero sidebar widget**: Skill library with confidence bars.
- 16 built-in slash commands: `/help`, `/plan`, `/why`, `/cost`, `/recipe`,
  `/test`, `/find`, `/voice`, `/theme`, `/resume`, `/clear`, `/auto`,
  `/default`, `/quit`, `/cost tool`, `/cost agent`.
- Differentiators built in:
  - Stacked context-budget bar (system / files / conversation / output).
  - Latency sparkline with TTFT + inter-token measurements.
  - Per-tool / per-subagent token + cost rollup table.
  - Typed `Plan` editor (reorder + edit before execution).
  - Per-hunk diff approval (`y/n/a/d/q`).
  - Permission gates with blast-radius preview.
  - Auto-test / auto-lint loop (`/test on`).
  - Recipes (Goose-style YAML) under `recipes/`.
  - Transcript search (`Ctrl+F`).
  - Dual-cursor composer (input + agent quick-replies).
  - Voice mode (`F9` push-to-talk; `pip install 'harness-tui[voice]'`).
  - Web mode (`--serve` via `textual-serve`).
  - SSH mode (`--ssh` via `asyncssh`).
- **Visual snapshot tests** in CI — every PR diffs the SVG-rendered TUI.

Mentat-specific commands: `/skill new`, `/skill list`, `/memory show <topic>`,
`/forget <pattern>`, `/privacy`.

See [`research/tui-state-of-the-art.md`](../../../research/tui-state-of-the-art.md)
and [`research/tui-framework-and-rollout.md`](../../../research/tui-framework-and-rollout.md)
for the design.

## License

MIT
