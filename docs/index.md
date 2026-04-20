---
layout: default
title: Mentat-Learn
---

# Mentat-Learn

> Self-improving personal assistant — multi-channel gateway, skill library, Honcho dialectic user model.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Status: MVP](https://img.shields.io/badge/status-walking--skeleton-brightgreen)](#)

## Design documents

- **[Architecture](architecture.md)** — components, data flow, invariants.
- **[Architecture tradeoffs](architecture-tradeoff.md)** — alternatives considered; explicit ROC of design choices.
- **[System design](system-design.md)** — APIs, schemas, deployment, scaling, SLOs.
- **[Blocks](blocks/)** — one file per major architectural block.

## Quickstart

```bash
make install
make test
make run
```

HTTP surface: `http://localhost:8008/docs`

## Docker

```bash
make docker-up
make docker-logs
make docker-down
```

## Context

Part of the **Harness Agentic AI Systems** design portfolio — ten walking-skeleton and design-only systems targeting measurable gaps in current public agent platforms.

---

Source: [GitHub repo](https://github.com/ndqkhanh/mentat-learn) · License: MIT
