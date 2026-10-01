"""
Health Endpoint Tests.

Verifies basic health status, service metadata, and safe operation without active secrets or models.
"""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient) -> None:
    """Verifies that root endpoint returns HTTP 200 and operational status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "version" in data
    assert "service" in data


def test_health_endpoint(client: TestClient) -> None:
    """Verifies that /api/v1/health returns HTTP 200, healthy status, and pending component map."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["implementation_phase"] == "Step 1 — Repository & Local Foundation"
    assert "components" in data
    components = data["components"]
    assert components["database"] == "pending_step_2_supabase"
    assert components["embedding_model"] == "pending_benchmark"
    assert components["gemini_api"] == "pending_step_7_rag"
    assert components["evidence_corpus"] == "pending_step_3_ingestion"
    assert components["subsystem_a"] == "pending_implementation"
    assert components["subsystem_b"] == "pending_implementation"
