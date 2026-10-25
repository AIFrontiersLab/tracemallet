import pytest
from fastapi.testclient import TestClient
from main import app, store

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_store():
    store.clear()

def test_ingest_and_get_trace():
    trace_id = "test-trace-1"
    resp = client.post("/ingest", json={
        "trace_id": trace_id,
        "spans": [{"name": "span1", "latency_ms": 10}]
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    resp_get = client.get(f"/trace/{trace_id}")
    assert resp_get.status_code == 200
    data = resp_get.json()
    assert data["span_count"] == 1
    assert data["total_latency_ms"] == 10.0

def test_multiple_spans():
    trace_id = "test-trace-2"
    spans = [
        {"name": "s1", "latency_ms": 5},
        {"name": "s2", "latency_ms": 15}
    ]
    resp = client.post("/ingest", json={
        "trace_id": trace_id,
        "spans": spans
    })
    assert resp.status_code == 200

    resp_get = client.get(f"/trace/{trace_id}")
    assert resp_get.status_code == 200
    data = resp_get.json()
    assert data["span_count"] == 2
    assert data["total_latency_ms"] == 20.0

def test_404_on_missing_trace():
    resp = client.get("/trace/nonexistent")
    assert resp.status_code == 404

def test_invalid_span_latency():
    resp = client.post("/ingest", json={
        "trace_id": "t1",
        "spans": [{"name": "s1", "latency_ms": -5}]
    })
    assert resp.status_code == 422
