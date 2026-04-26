import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app
from app.repositories.session_store import session_store
from app.schemas.setup import SessionCreateRequest
from app.services.setup_service import SetupService


def _reset_store() -> None:
    session_store.reset()


@pytest.fixture(autouse=True)
def reset_session_store():
    _reset_store()
    yield
    _reset_store()


@pytest.fixture
def sample_data_dir() -> Path:
    return ROOT / "sample_data"


@pytest.fixture
def sample_payloads(sample_data_dir: Path) -> dict:
    payload_file = sample_data_dir / "payloads" / "setup_payloads.json"
    return json.loads(payload_file.read_text(encoding="utf-8"))


@pytest.fixture
async def seeded_session(sample_payloads: dict):
    service = SetupService()
    return await service.create_session(
        SessionCreateRequest(
            user_name=sample_payloads["session"]["user_name"],
            target_role=sample_payloads["session"]["target_role"],
            experience_level=sample_payloads["session"]["experience_level"],
        )
    )


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
