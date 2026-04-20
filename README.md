# Mentat-Learn

> Self-improving personal assistant — multi-channel gateway, skill library, Honcho dialectic user model.

Walking-skeleton implementation of the [Mentat-Learn design](docs/architecture.md). One coherent persona the user meets across multiple channels (Slack, WhatsApp, Telegram, email, iMessage, web) that gets more capable over time by extracting reusable procedures from completed workflows into a growing skill library. Fuses ideas from OpenClaw (multi-channel gateway), SemaClaw (DAG teams + SOUL.md persona + PermissionBridge), and Hermes Agent (closed skill-learning loop + Honcho dialectic user model).

Design docs: [docs/architecture.md](docs/architecture.md) · [docs/architecture-tradeoff.md](docs/architecture-tradeoff.md) · [docs/system-design.md](docs/system-design.md) · [blocks/](docs/blocks/).

## Quickstart

```bash
make install
make test
make run
```

API docs served at `http://localhost:8008/docs`.

## Docker

```bash
make docker-up
make docker-logs
make docker-down
```

## License

[MIT](LICENSE)
