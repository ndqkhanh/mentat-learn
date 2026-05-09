"""Mentat-Learn brand — Twilight blue + memory rose, sigil logo."""
from __future__ import annotations

from harness_tui.theme import Theme
from harness_tui.themes import catppuccin_mocha

MENTAT_LOGO = r"""
       [bold #1E3A8A]◆[/]
      [bold #1E3A8A]╱[/][bold #F472B6]│[/][bold #1E3A8A]╲[/]
     [bold #1E3A8A]◆[/] [bold #F472B6]M[/] [bold #1E3A8A]◆[/]   [dim]Mentat-Learn[/]
      [bold #1E3A8A]╲[/][bold #F472B6]│[/][bold #1E3A8A]╱[/]
       [bold #1E3A8A]◆[/]
""".strip("\n")


def mentat_theme() -> Theme:
    return catppuccin_mocha().with_brand(
        name="mentat-learn",
        primary="#60A5FA",
        primary_alt="#1E3A8A",
        accent="#F472B6",
        ascii_logo=MENTAT_LOGO,
        spinner_frames=("◇", "◆", "◇", "◆"),
    )
