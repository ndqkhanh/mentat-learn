"""FastAPI surface for Mentat-Learn."""
from __future__ import annotations

import uuid
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .gateway import Gateway, InboundMessage, InMemoryChannel
from .loop import MentatAgent
from .models import ConsentFlags, SkillRecord, UserProfile

app = FastAPI(
    title="Mentat-Learn",
    description="Self-improving personal assistant — unified gateway, four-layer memory, skill extractor, dialectic user modeling.",
    version="0.1.0",
)

_profile = UserProfile()
_profile.channels_enabled["in-memory"] = ConsentFlags(
    persistent_memory=True,
    scheduled_automations=True,
)

_gateway = Gateway()
_channel = InMemoryChannel(name="in-memory")
_gateway.register(_channel)

_agent = MentatAgent(profile=_profile, gateway=_gateway)


class TurnRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    channel: str = "in-memory"


class TurnResponse(BaseModel):
    reply: str
    session_id: str
    channel: str
    matched_skills: list[str]
    memory_writes: int
    dialectic_updates: list[dict]
    pii_redactions: int


class SkillRequest(BaseModel):
    name: str
    description: str
    body_md: str
    required_tools: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class ConsentRequest(BaseModel):
    channel: str
    persistent_memory: bool = False
    cross_channel_share: bool = False
    dialectic_modeling: bool = False
    scheduled_automations: bool = False


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "mentat-learn"}


@app.get("/v1/me")
def me() -> dict[str, Any]:
    return {
        "user_id": _profile.id,
        "channels": list(_profile.channels_enabled),
        "soul_md": _profile.soul_md,
    }


@app.post("/v1/me/consent")
def update_consent(req: ConsentRequest) -> dict:
    _agent.privacy.set_consent(
        req.channel,
        ConsentFlags(
            persistent_memory=req.persistent_memory,
            cross_channel_share=req.cross_channel_share,
            dialectic_modeling=req.dialectic_modeling,
            scheduled_automations=req.scheduled_automations,
        ),
    )
    return {"channel": req.channel, "updated": True}


@app.post("/v1/skills", response_model=SkillRecord)
def create_skill(req: SkillRequest) -> SkillRecord:
    try:
        return _agent.library.register(
            SkillRecord(
                name=req.name,
                description=req.description,
                body_md=req.body_md,
                required_tools=req.required_tools,
                tags=req.tags,
                source="user-authored",
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@app.get("/v1/skills")
def list_skills() -> dict:
    return {
        "count": len(_agent.library.all()),
        "skills": [
            {"id": s.id, "name": s.name, "description": s.description,
             "version": s.version, "use_count": s.use_count,
             "success_rate": s.success_rate, "subsumed_by": s.subsumed_by}
            for s in _agent.library.all()
        ],
    }


@app.post("/v1/turn", response_model=TurnResponse)
def turn(req: TurnRequest) -> TurnResponse:
    msg = InboundMessage(
        id=uuid.uuid4().hex[:12],
        user_id=req.user_id or _profile.id,
        session_id=req.session_id or uuid.uuid4().hex[:12],
        channel=req.channel,
        text=req.text,
    )
    result = _agent.handle(msg)
    return TurnResponse(
        reply=result.reply,
        session_id=result.session_id,
        channel=result.channel,
        matched_skills=[m.skill.name for m in result.matched_skills],
        memory_writes=result.memory_writes,
        dialectic_updates=[
            {"dimension": u.dimension, "value": u.value, "confidence": u.confidence}
            for u in result.dialectic_updates
        ],
        pii_redactions=result.pii_redactions,
    )


@app.post("/v1/self-eval")
def run_self_eval() -> dict:
    report = _agent.evaluator.run()
    return {
        "cycle": report.cycle,
        "persona_drift_score": report.persona_drift_score,
        "privacy_incidents": report.privacy_incidents,
        "skills": [
            {"name": s.name, "use_count": s.use_count,
             "success_rate": s.success_rate, "status": s.status}
            for s in report.skills
        ],
    }
