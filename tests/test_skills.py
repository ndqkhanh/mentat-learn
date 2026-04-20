import pytest
from mentat_learn.models import SkillRecord
from mentat_learn.skills import SkillExtractor, SkillLibrary


def _skill(name: str, description: str, body: str = "# steps\n") -> SkillRecord:
    return SkillRecord(name=name, description=description, body_md=body)


def test_register_and_match_skill():
    lib = SkillLibrary()
    lib.register(_skill("weekly-review", "Draft the weekly review from calendar and tasks"))
    matches = lib.match("draft my weekly review")
    assert matches and matches[0].skill.name == "weekly-review"


def test_duplicate_name_rejected():
    lib = SkillLibrary()
    lib.register(_skill("x", "desc"))
    with pytest.raises(ValueError, match="already exists"):
        lib.register(_skill("x", "other"))


def test_match_respects_similarity_threshold():
    lib = SkillLibrary()
    lib.register(_skill("review-code", "review code diff for issues"))
    # Completely unrelated query → no match
    assert lib.match("what's the weather in Tokyo") == []


def test_subsumed_skills_not_preferred_in_match():
    lib = SkillLibrary()
    base = lib.register(_skill("a", "alpha skill"))
    composite = lib.register(_skill("b", "beta composite containing alpha"))
    base.subsumed_by = composite.id
    lib.update(base)
    matches = lib.match("alpha")
    returned = [m.skill.id for m in matches]
    assert base.id not in returned
    assert composite.id in returned


def test_record_use_updates_stats():
    lib = SkillLibrary()
    s = lib.register(_skill("x", "desc"))
    lib.record_use(s.id, success=True)
    lib.record_use(s.id, success=False)
    assert s.use_count == 2
    assert s.success_rate == 0.5


def test_body_cache_lru_works():
    lib = SkillLibrary(body_cache_size=2)
    a = lib.register(_skill("a", "alpha"))
    b = lib.register(_skill("b", "beta"))
    c = lib.register(_skill("c", "gamma"))
    # Accessing a should bring it to front, then adding d would evict b
    assert lib.body(a.id) is not None
    d = lib.register(_skill("d", "delta"))
    assert len(lib._body_cache) == 2


def test_extractor_skips_single_tool_sequences():
    lib = SkillLibrary()
    ex = SkillExtractor(lib)
    assert ex.extract(task_summary="x", tool_sequence=["read"], outcome="success") is None


def test_extractor_skips_failed_outcome():
    lib = SkillLibrary()
    ex = SkillExtractor(lib)
    assert ex.extract(task_summary="x", tool_sequence=["a", "b"], outcome="failed") is None


def test_extractor_creates_new_skill_on_success():
    lib = SkillLibrary()
    ex = SkillExtractor(lib)
    skill = ex.extract(
        task_summary="draft weekly review",
        tool_sequence=["read_calendar", "cluster_events", "draft_prose"],
        outcome="success",
    )
    assert skill is not None
    assert "read_calendar" in skill.required_tools


def test_extractor_refines_existing_skill():
    lib = SkillLibrary()
    ex = SkillExtractor(lib)
    first = ex.extract(
        task_summary="draft weekly review",
        tool_sequence=["a", "b"],
        outcome="success",
    )
    refined = ex.extract(
        task_summary="draft weekly review",
        tool_sequence=["a", "b", "c"],
        outcome="success",
    )
    assert refined is first
    assert refined.version == 2


def test_compression_triggers_on_cooccurrence():
    lib = SkillLibrary()
    ex = SkillExtractor(lib)
    a = lib.register(_skill("alpha", "alpha"))
    b = lib.register(_skill("beta", "beta"))
    for _ in range(3):
        lib.record_co_occurrence((a.id, b.id))
    composite = ex.compress()
    assert composite is not None
    # Base skills marked subsumed
    assert a.subsumed_by == composite.id
    assert b.subsumed_by == composite.id
