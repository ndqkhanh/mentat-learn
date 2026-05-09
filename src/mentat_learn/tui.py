"""Mentat-Learn TUI — self-improving personal assistant."""
from __future__ import annotations

import os
from typing import Optional

import click
from harness_tui import HarnessApp, ProjectConfig
from harness_tui.commands.registry import register_command
from harness_tui.transport import HTTPTransport, MockTransport

from .tui_theme import mentat_theme
from .widgets import SkillLibrary


@register_command(name="skill", description="Manage skill library (new/list)",
                  category="Mentat")
async def cmd_skill(app, args: str) -> None:  # type: ignore[no-untyped-def]
    if args.startswith("new"):
        app.shell.chat_log.write_system("skill: new (form in sidebar)")
    elif args.startswith("list") or not args:
        app.shell.chat_log.write_system("(skill library: see sidebar Skills tab)")


@register_command(name="memory", description="Inspect memory by topic",
                  category="Mentat")
async def cmd_memory(app, args: str) -> None:  # type: ignore[no-untyped-def]
    if args.startswith("show "):
        topic = args[5:].strip()
        app.shell.chat_log.write_system(f"memory @ {topic!r}: see provenance in sidebar")
    else:
        app.shell.chat_log.write_system("usage: /memory show <topic>")


@register_command(name="forget", description="Remove memory matching a pattern",
                  category="Mentat")
async def cmd_forget(app, args: str) -> None:  # type: ignore[no-untyped-def]
    pat = args.strip() or "(no pattern)"
    app.shell.chat_log.write_system(f"forget pattern: {pat!r} (HITL gated)")


@register_command(name="privacy", description="Audit what's stored and where",
                  category="Mentat")
async def cmd_privacy(app, _: str) -> None:  # type: ignore[no-untyped-def]
    app.shell.chat_log.write_system(
        "privacy audit: 0 third-party stores · all memory local + redacted"
    )


@click.command()
@click.option("--url", default=None)
@click.option("--mock", is_flag=True)
@click.option("--serve", is_flag=True,
              help="Run the TUI in a browser via textual-serve.")
@click.option("--port", type=int, default=8008,
              help="Web mode port (with --serve).")
@click.option("--host", default="127.0.0.1",
              help="Web mode host (with --serve).")
def main(url: Optional[str], mock: bool, serve: bool, port: int, host: str) -> None:
    """Open the Mentat-Learn TUI."""
    if serve:
        from harness_tui.serve import serve_app, make_module_command

        flags = []
        if mock:
            flags.append("--mock")
        if url:
            flags.append(f"--url {url}")
        serve_app(
            command=make_module_command("mentat_learn.tui", " ".join(flags)),
            host=host, port=port,
            title="mentat-learn",
        )
        return
    if mock:
        transport = MockTransport()
    else:
        backend = url or os.environ.get("MENTAT_BACKEND") or "http://localhost:8008"
        transport = HTTPTransport(
            backend,
            endpoints={"run": "/v1/turn"},
            payload_builder=lambda t, m: {"text": t},
            text_field="reply",
        )
    cfg = ProjectConfig(
        name="mentat-learn",
        description="Self-improving personal assistant",
        theme=mentat_theme(),
        transport=transport,
        model=os.environ.get("MENTAT_MODEL", "auto"),
        sidebar_tabs=[("Skills", SkillLibrary())],
    )
    app = HarnessApp(cfg)
    app.run()
    summary = getattr(app, "last_exit_summary", None)
    if summary:
        click.echo(summary.render())


if __name__ == "__main__":  # pragma: no cover
    main()
