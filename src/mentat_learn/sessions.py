"""Session store + cross-channel linkage (explicit user confirm)."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Session:
    id: str
    user_id: str
    channel: str
    state: str = "active"                        # active | idle | closed
    started_at: float = field(default_factory=time.time)
    last_activity_at: float = field(default_factory=time.time)
    linked_sessions: list[str] = field(default_factory=list)
    turn_count: int = 0


class SessionStore:
    def __init__(self, *, idle_timeout_s: float = 3600.0) -> None:
        self._by_id: dict[str, Session] = {}
        self._idle_timeout_s = idle_timeout_s

    def get_or_create(self, *, user_id: str, channel: str, session_id: Optional[str] = None) -> Session:
        if session_id and session_id in self._by_id:
            sess = self._by_id[session_id]
            self._reactivate(sess)
            return sess
        sess = Session(
            id=session_id or uuid.uuid4().hex[:12],
            user_id=user_id,
            channel=channel,
        )
        self._by_id[sess.id] = sess
        return sess

    def bump(self, session_id: str) -> None:
        sess = self._by_id.get(session_id)
        if sess is None:
            return
        sess.turn_count += 1
        sess.last_activity_at = time.time()
        if sess.state == "idle":
            sess.state = "active"

    def sweep_idle(self) -> int:
        """Mark sessions as idle if past the timeout. Return count marked."""
        count = 0
        now = time.time()
        for sess in self._by_id.values():
            if sess.state == "active" and (now - sess.last_activity_at) > self._idle_timeout_s:
                sess.state = "idle"
                count += 1
        return count

    def close(self, session_id: str) -> bool:
        sess = self._by_id.get(session_id)
        if sess is None:
            return False
        sess.state = "closed"
        sess.last_activity_at = time.time()
        return True

    def link(self, sid_a: str, sid_b: str) -> bool:
        a = self._by_id.get(sid_a)
        b = self._by_id.get(sid_b)
        if a is None or b is None:
            return False
        if sid_b not in a.linked_sessions:
            a.linked_sessions.append(sid_b)
        if sid_a not in b.linked_sessions:
            b.linked_sessions.append(sid_a)
        return True

    def get(self, session_id: str) -> Optional[Session]:
        return self._by_id.get(session_id)

    def active(self) -> list[Session]:
        return [s for s in self._by_id.values() if s.state == "active"]

    def all(self) -> list[Session]:
        return list(self._by_id.values())

    def delete(self, session_id: str) -> bool:
        return self._by_id.pop(session_id, None) is not None

    def _reactivate(self, sess: Session) -> None:
        sess.last_activity_at = time.time()
        if sess.state == "idle":
            sess.state = "active"
