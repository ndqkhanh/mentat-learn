from mentat_learn.models import ConsentFlags, UserProfile
from mentat_learn.privacy import PIIRedactor, PrivacyScope


def test_redacts_email():
    r = PIIRedactor().redact("contact me at alice@example.com please")
    assert "[EMAIL]" in r.text
    assert any(k == "email" for k, _ in r.redactions)


def test_redacts_phone_number():
    r = PIIRedactor().redact("call (415) 555-1234 tomorrow")
    assert "[PHONE]" in r.text


def test_redacts_credit_card_shape():
    r = PIIRedactor().redact("card 4111 1111 1111 1111 expires soon")
    assert "[CREDIT_CARD]" in r.text


def test_redacts_ssn():
    r = PIIRedactor().redact("ssn 123-45-6789")
    assert "[SSN]" in r.text


def test_redacts_jwt_like_token():
    token = "eyJabc.def.ghi"
    r = PIIRedactor().redact(f"Authorization: Bearer {token}")
    assert "[JWT]" in r.text


def test_no_redactions_on_clean_text():
    r = PIIRedactor().redact("tell me about kras in cancer")
    assert r.redactions == []
    assert r.text == "tell me about kras in cancer"


def test_consent_defaults_deny():
    p = UserProfile()
    scope = PrivacyScope(p)
    assert scope.can_write_memory("slack") is False
    assert scope.can_share_cross_channel("slack") is False
    assert scope.can_model_dialectic("slack") is False


def test_consent_set_applies():
    p = UserProfile()
    scope = PrivacyScope(p)
    scope.set_consent("slack", ConsentFlags(persistent_memory=True))
    assert scope.can_write_memory("slack") is True


def test_any_consented_channel_returns_first():
    p = UserProfile()
    scope = PrivacyScope(p)
    scope.set_consent("a", ConsentFlags())  # no memory
    scope.set_consent("b", ConsentFlags(persistent_memory=True))
    assert scope.any_consented_channel() == "b"
