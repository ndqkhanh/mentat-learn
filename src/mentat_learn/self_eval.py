"""Periodic self-eval: skill correctness, persona drift, privacy compliance."""
from __future__ import annotations

from dataclasses import dataclass, field

from .memory import FourLayerMemory
from .skills import SkillLibrary


@dataclass
class SkillStat:
    skill_id: str
    name: str
    use_count: int
    success_rate: float
    status: str                             # healthy | flagged | retired


@dataclass
class SelfEvalReport:
    cycle: int
    skills: list[SkillStat] = field(default_factory=list)
    persona_drift_score: float = 0.0
    privacy_incidents: int = 0
    dialectic_stable: bool = True


class SelfEvaluator:
    """Evaluate every N tasks; retire low-success skills; flag drift."""

    DEFAULT_CADENCE_TASKS = 15
    MIN_USES_FOR_RETIREMENT = 3
    RETIREMENT_SUCCESS_THRESHOLD = 0.40
    FLAG_SUCCESS_THRESHOLD = 0.60

    def __init__(self, library: SkillLibrary, memory: FourLayerMemory) -> None:
        self.library = library
        self.memory = memory
        self.cycle = 0
        self._task_counter = 0

    def should_run(self) -> bool:
        return self._task_counter > 0 and self._task_counter % self.DEFAULT_CADENCE_TASKS == 0

    def note_task(self) -> None:
        self._task_counter += 1

    def run(self) -> SelfEvalReport:
        self.cycle += 1
        report = SelfEvalReport(cycle=self.cycle)
        retire_ids: list[str] = []
        for skill in self.library.all(include_subsumed=False):
            sr = skill.success_rate if skill.success_rate is not None else 0.75
            status = "healthy"
            if skill.use_count >= self.MIN_USES_FOR_RETIREMENT:
                if sr < self.RETIREMENT_SUCCESS_THRESHOLD:
                    status = "retired"
                    retire_ids.append(skill.id)
                elif sr < self.FLAG_SUCCESS_THRESHOLD:
                    status = "flagged"
            report.skills.append(
                SkillStat(
                    skill_id=skill.id,
                    name=skill.name,
                    use_count=skill.use_count,
                    success_rate=sr,
                    status=status,
                )
            )
        for sid in retire_ids:
            self.library.disable(sid)
        return report
