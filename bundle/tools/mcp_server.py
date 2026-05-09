"""Mentat-Learn MCP server stub.

Tools published:

- ``mentat.recall(user, query, top_k)`` — four-tier memory recall.
- ``mentat.remember(user, fact, tier)`` — write to a specific tier.
- ``mentat.dialectic_query(user, key)`` — query the dialectic user model.
- ``mentat.extract_skills()`` — kick the closed-loop extractor.
- ``mentat.redact(text)`` — apply the privacy redactor.
- ``mentat.health()`` — adapter health.
"""
from __future__ import annotations

import json
import sys


def main() -> int:
    line = sys.stdin.readline()
    if not line.strip():
        print(json.dumps({"error": "no input"}))
        return 0
    req = json.loads(line)
    tool = req.get("tool", "mentat.health")
    args = req.get("args") or {}
    if tool == "mentat.recall":
        print(json.dumps({"tool": tool, "result": {"hits": [], "tier_used": "episodic"}}))
    elif tool == "mentat.remember":
        print(json.dumps({"tool": tool, "result": {"stored": True, "tier": args.get("tier", "episodic")}}))
    elif tool == "mentat.dialectic_query":
        print(json.dumps({"tool": tool, "result": {"value": None}}))
    elif tool == "mentat.extract_skills":
        print(json.dumps({"tool": tool, "result": {"promoted": 0, "demoted": 0}}))
    elif tool == "mentat.redact":
        print(json.dumps({"tool": tool, "result": {"text": "<redacted>"}}))
    elif tool == "mentat.health":
        print(json.dumps({"tool": tool, "result": {"ok": True}}))
    else:
        print(json.dumps({"tool": tool, "error": f"unknown tool {tool}"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
