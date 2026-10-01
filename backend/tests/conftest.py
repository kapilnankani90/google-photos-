"""
Pytest Configuration and Fixtures.

Governed by: part1_discovery_engine_implementation_spec.md (Section 26)
Provides reusable test fixtures including FastAPI TestClient.
"""

import sys
from pathlib import Path
from typing import Generator
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """TestClient fixture for FastAPI endpoint testing."""
    with TestClient(app) as test_client:
        yield test_client
