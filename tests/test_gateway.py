import pytest
from mentat_learn.gateway import Gateway, InMemoryChannel, OutboundMessage


def test_register_and_channels_listed():
    gw = Gateway()
    gw.register(InMemoryChannel("slack"))
    gw.register(InMemoryChannel("telegram"))
    assert gw.channels() == ["slack", "telegram"]


def test_duplicate_registration_rejected():
    gw = Gateway()
    gw.register(InMemoryChannel("x"))
    with pytest.raises(ValueError, match="already registered"):
        gw.register(InMemoryChannel("x"))


def test_empty_channel_name_rejected():
    gw = Gateway()
    with pytest.raises(ValueError, match="must set .channel"):
        gw.register(InMemoryChannel(""))


def test_drain_inbound_collects_from_all_channels():
    gw = Gateway()
    slack = InMemoryChannel("slack")
    tg = InMemoryChannel("telegram")
    gw.register(slack)
    gw.register(tg)
    slack.push("u1", "s1", "hi from slack")
    tg.push("u1", "s2", "hi from telegram")
    drained = gw.drain_inbound()
    channels = sorted(m.channel for m in drained)
    assert channels == ["slack", "telegram"]


def test_send_routes_to_correct_adapter():
    gw = Gateway()
    slack = InMemoryChannel("slack")
    gw.register(slack)
    gw.send(OutboundMessage(in_reply_to="x", user_id="u", session_id="s",
                            channel="slack", text="reply"))
    assert len(slack.sent()) == 1


def test_send_unknown_channel_raises():
    gw = Gateway()
    with pytest.raises(LookupError, match="no adapter"):
        gw.send(OutboundMessage(in_reply_to="x", user_id="u", session_id="s",
                                channel="nope", text="r"))
