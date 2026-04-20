from fastapi.testclient import TestClient
from mentat_learn.app import app

client = TestClient(app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["service"] == "mentat-learn"


def test_me_returns_profile():
    r = client.get("/v1/me")
    assert r.status_code == 200
    body = r.json()
    assert "user_id" in body
    assert "in-memory" in body["channels"]


def test_turn_without_skills_uses_first_principles():
    r = client.post("/v1/turn", json={"text": "tell me about the moon"})
    assert r.status_code == 200
    body = r.json()
    assert "[first-principles]" in body["reply"]
    assert body["matched_skills"] == []


def test_register_skill_and_match():
    created = client.post("/v1/skills", json={
        "name": "email-triage-" + "x" * 4,
        "description": "triage recent emails by topic",
        "body_md": "# Steps\n1. fetch emails\n2. cluster\n3. draft replies",
    })
    assert created.status_code == 200
    r = client.post("/v1/turn", json={"text": "triage my emails for me"})
    assert r.json()["matched_skills"]   # non-empty


def test_duplicate_skill_rejected():
    first = client.post("/v1/skills", json={
        "name": "unique-one",
        "description": "first one",
        "body_md": "body",
    })
    assert first.status_code == 200
    second = client.post("/v1/skills", json={
        "name": "unique-one",
        "description": "another",
        "body_md": "body",
    })
    assert second.status_code == 409


def test_consent_update():
    r = client.post("/v1/me/consent", json={
        "channel": "in-memory",
        "persistent_memory": True,
        "dialectic_modeling": True,
    })
    assert r.status_code == 200
    assert r.json()["updated"] is True


def test_self_eval_returns_report():
    r = client.post("/v1/self-eval")
    assert r.status_code == 200
    body = r.json()
    assert "cycle" in body
    assert "skills" in body
