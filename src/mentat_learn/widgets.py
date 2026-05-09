"""Mentat-Learn project widgets — skill library with confidence bars."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from rich.markup import escape
from rich.panel import Panel
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import ListItem, ListView, Static


@dataclass
class Skill:
    name: str
    description: str
    confidence: float  # 0.0 .. 1.0
    uses: int = 0
    last_used: str = ""
    source_sessions: List[str] = field(default_factory=list)


_DEMO_SKILLS = [
    Skill("explain-codebase", "Walk through a repo's entry points + tests",
          confidence=0.92, uses=27, last_used="2026-05-09",
          source_sessions=["s_a1f", "s_b22", "s_c08"]),
    Skill("fix-flaky-test", "Bisect a flake and propose a minimal fix",
          confidence=0.78, uses=12, last_used="2026-05-08"),
    Skill("schema-migration", "Plan a NOT-NULL column add on a 50M-row table",
          confidence=0.66, uses=4),
    Skill("retro-summary", "Summarize a session as user/agent/decisions/blockers",
          confidence=0.85, uses=18, last_used="2026-05-09"),
    Skill("budget-alarm", "Notify when monthly spend crosses 80% of cap",
          confidence=0.43, uses=2),
]


def _bar(confidence: float, width: int = 14) -> Text:
    filled = max(0, min(width, int(round(confidence * width))))
    text = Text()
    color = "green" if confidence > 0.75 else ("yellow" if confidence > 0.5 else "red")
    text.append("█" * filled, style=color)
    text.append("░" * (width - filled), style="dim")
    text.append(f"  {int(confidence * 100):>3d}%", style=color)
    return text


class SkillLibrary(Vertical):
    DEFAULT_CSS = """
    SkillLibrary {
        height: 1fr;
    }
    SkillLibrary ListView {
        height: 50%;
        background: $bg;
    }
    SkillLibrary #detail {
        height: 1fr;
        padding: 1;
        background: $bg_alt;
        color: $fg_muted;
    }
    """

    def __init__(self, skills: List[Skill] | None = None) -> None:
        super().__init__()
        self.skills = list(skills) if skills is not None else list(_DEMO_SKILLS)

    def compose(self) -> ComposeResult:
        items = []
        for i, sk in enumerate(self.skills):
            line = Text()
            line.append("▸ ", style="dim")
            line.append(sk.name, style="bold")
            line.append("  ")
            line.append_text(_bar(sk.confidence, 8))
            items.append(ListItem(Static(line), id=f"sk-{i}"))
        yield ListView(*items, id="skills")
        yield Static(self._detail(0), id="detail")

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item is None:
            return
        idx = int((event.item.id or "sk-0")[3:])
        self.query_one("#detail", Static).update(self._detail(idx))

    def _detail(self, idx: int) -> Panel:
        if not self.skills:
            return Panel(Text("(no skills acquired)", style="dim"), border_style="dim")
        sk = self.skills[idx]
        body = Text()
        body.append(sk.name, style="bold")
        body.append("\n")
        body.append(escape(sk.description), style="dim")
        body.append("\n\nconfidence:  ", style="bold")
        body.append_text(_bar(sk.confidence))
        body.append(f"\nuses:        {sk.uses}", style="default")
        if sk.last_used:
            body.append(f"\nlast used:   {sk.last_used}", style="dim")
        if sk.source_sessions:
            body.append("\nsessions:    ", style="dim")
            body.append(", ".join(sk.source_sessions), style="cyan")
        return Panel(body, title="[bold]skill[/]", title_align="left",
                     border_style="magenta")
