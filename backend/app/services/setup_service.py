from datetime import datetime
from uuid import uuid4

from app.core.exceptions import ResourceNotFoundError
from app.repositories.session_store import session_store
from app.schemas.common import SessionStatus, StepName
from app.schemas.setup import SessionCreateRequest, SessionDetailResponse, SessionPayload


class SetupService:
    async def create_session(self, payload: SessionCreateRequest) -> SessionPayload:
        session_id = uuid4()
        record = session_store.create_session(session_id, payload)
        return SessionPayload(
            session_id=session_id,
            status=SessionStatus(record["status"]),
            current_step=StepName(record["current_step"]),
            created_at=record["created_at"],
        )

    async def get_session(self, session_id) -> SessionDetailResponse:
        record = session_store.get_session(session_id)
        if record is None:
            raise ResourceNotFoundError(f"Session '{session_id}' was not found.")
        return SessionDetailResponse(
            session_id=record["session_id"],
            target_role=record["target_role"],
            status=SessionStatus(record["status"]),
            current_step=StepName(record["current_step"]),
        )
