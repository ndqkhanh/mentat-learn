from mentat_learn.gateway import Gateway, InMemoryChannel, InboundMessage
from mentat_learn.loop import MentatAgent
from mentat_learn.models import ConsentFlags, SkillRecord, UserProfile


def _agent(with_consent: bool = True, dialectic: bool = False) -> MentatAgent:
    profile = UserProfile()
    if with_consent:
        profile.channels_enabled["in-memory"] = ConsentFlags(
            persistent_memory=True, dialectic_modeling=dialectic,
        )
    gw = Gateway()
    gw.register(InMemoryChannel("in-memory"))
    return MentatAgent(profile=profile, gateway=gw)


def _msg(text: str, sid: str = "s1", channel: str = "in-memory") -> InboundMessage:
    return InboundMessage(
        id="m1", user_id="u1", session_id=sid, channel=channel, text=text,
    )


def test_turn_without_skill_uses_first_principles():
    agent = _agent()
    result = agent.handle(_msg("tell me about quantum gravity"))
    assert "[first-principles]" in result.reply
    assert result.matched_skills == []


def test_turn_matches_skill_when_description_similar():
    agent = _agent()
    agent.library.register(SkillRecord(
        name="weekly-review",
        description="draft the weekly review from calendar events and tasks",
        body_md="# Steps\n1. fetch calendar\n2. summarize",
    ))
    result = agent.handle(_msg("draft my weekly review from calendar"))
    assert result.matched_skills
    assert "[skill=weekly-review]" in result.reply


def test_preference_recorded_when_consent_given():
    agent = _agent(with_consent=True)
    result = agent.handle(_msg("I prefer bullet-point summaries"))
    assert result.memory_writes == 1
    prefs = agent.memory.facts.of_kind("preference")
    assert prefs and "bullet" in prefs[0].content


def test_preference_not_recorded_without_consent():
    agent = _agent(with_consent=False)
    result = agent.handle(_msg("I prefer bullet-point summaries"))
    assert result.memory_writes == 0
    assert agent.memory.facts.of_kind("preference") == []


def test_pii_redactions_counted():
    agent = _agent()
    result = agent.handle(_msg("email me at alice@example.com please"))
    assert result.pii_redactions >= 1
    # session memory stored the redacted version
    turns = agent.memory.get_or_create_session("s1", "in-memory").turns
    user_turn = next(t for t in turns if t["role"] == "user")
    assert "[EMAIL]" in user_turn["text"]


def test_dialectic_updates_when_consented():
    agent = _agent(dialectic=True)
    result = agent.handle(_msg("tldr please"))
    dims = [u.dimension for u in result.dialectic_updates]
    assert "communication_preference" in dims


def test_dialectic_silent_without_consent():
    agent = _agent(dialectic=False)
    result = agent.handle(_msg("tldr please"))
    assert result.dialectic_updates == []


def test_outbound_delivered_via_gateway():
    agent = _agent()
    agent.handle(_msg("hi"))
    sent = agent.gateway.get("in-memory").sent()
    assert len(sent) == 1
    assert sent[0].text.startswith("[first-principles]") or sent[0].text.startswith("[skill=")


def test_session_bumped_on_multiple_turns():
    agent = _agent()
    agent.handle(_msg("first"))
    agent.handle(_msg("second"))
    sess = agent.sessions.get("s1")
    assert sess.turn_count == 2
