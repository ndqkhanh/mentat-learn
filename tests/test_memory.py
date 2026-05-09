import time

from mentat_learn.memory import Fact, FourLayerMemory
from mentat_learn.skills import SkillLibrary


def test_add_fact_and_retrieve_by_kind():
    lib = SkillLibrary()
    mem = FourLayerMemory(lib)
    mem.facts.add_new("user prefers Python", kind="preference")
    mem.facts.add_new("deadline Friday", kind="fact")
    assert len(mem.facts.of_kind("preference")) == 1
    assert len(mem.facts.of_kind("fact")) == 1


def test_search_facts_with_keywords():
    lib = SkillLibrary()
    mem = FourLayerMemory(lib)
    mem.facts.add_new("prefers terse emails", kind="preference")
    mem.facts.add_new("likes pytest framework", kind="preference")
    mem.facts.add_new("unrelated weather note", kind="fact")
    results = mem.facts.search("pytest")
    assert len(results) == 1
    assert "pytest" in results[0].content


def test_session_memory_appends_turns():
    lib = SkillLibrary()
    mem = FourLayerMemory(lib)
    mem.append_turn("s1", "slack", role="user", text="hello")
    mem.append_turn("s1", "slack", role="assistant", text="hi")
    sess = mem.get_or_create_session("s1", "slack")
    assert len(sess.turns) == 2
    assert sess.turns[0]["role"] == "user"


def test_dialectic_disabled_by_default_is_silent():
    lib = SkillLibrary()
    mem = FourLayerMemory(lib)
    mem.set_dialectic("expertise_level", "expert")
    assert mem.dialectic_summary() == ""


def test_dialectic_enabled_records_updates():
    lib = SkillLibrary()
    mem = FourLayerMemory(lib, dialectic_enabled=True)
    mem.set_dialectic("expertise_level", "expert", 0.8)
    summary = mem.dialectic_summary()
    assert "expertise_level=expert" in summary


def test_expired_facts_filtered_by_default():
    lib = SkillLibrary()
    mem = FourLayerMemory(lib)
    mem.facts.add_new("stale fact", expires_at=time.time() - 10)
    mem.facts.add_new("fresh fact")
    active = [f.content for f in mem.facts.all()]
    assert "fresh fact" in active
    assert "stale fact" not in active
    # but retrievable with include_expired=True
    all_with_expired = [f.content for f in mem.facts.all(include_expired=True)]
    assert "stale fact" in all_with_expired


def test_forget_session_removes_it():
    lib = SkillLibrary()
    mem = FourLayerMemory(lib)
    mem.append_turn("s1", "slack", "user", "hi")
    assert mem.forget_session("s1") is True
    assert "s1" not in mem.sessions


def test_forget_all_clears_everything():
    lib = SkillLibrary()
    mem = FourLayerMemory(lib, dialectic_enabled=True)
    mem.facts.add_new("x")
    mem.append_turn("s1", "slack", "user", "hi")
    mem.set_dialectic("d", "v")
    mem.forget_all()
    assert mem.facts.all() == []
    assert mem.sessions == {}
    assert mem.dialectic == {}
