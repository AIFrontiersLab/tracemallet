from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(title="TraceIngest MVP")

# In-memory store: trace_id -> list of spans
store: dict = {}

class SpanInput(BaseModel):
    name: str = Field(..., min_length=1)
    latency_ms: float = Field(..., ge=0)

class IngestRequest(BaseModel):
    trace_id: str = Field(..., min_length=1)
    spans: List[SpanInput]

class TraceResponse(BaseModel):
    trace_id: str
    span_count: int
    total_latency_ms: float
    spans: List[SpanInput]

@app.post("/ingest")
def ingest(request: IngestRequest):
    trace_id = request.trace_id
    if trace_id not in store:
        store[trace_id] = []
    store[trace_id].extend(request.spans)
    return {"status": "ok", "trace_id": trace_id}

@app.get("/trace/{trace_id}")
def get_trace(trace_id: str):
    spans = store.get(trace_id)
    if not spans:
        raise HTTPException(status_code=404, detail="Trace not found")
    total_latency = sum(s.latency_ms for s in spans)
    return TraceResponse(
        trace_id=trace_id,
        span_count=len(spans),
        total_latency_ms=total_latency,
        spans=spans
    )

def demo():
    import httpx
    c = httpx.Client(base_url="http://test")
    # Ingest
    r1 = c.post("/ingest", json={"trace_id": "d1", "spans": [{"name": "s1", "latency_ms": 10}]})
    print(f"Ingest Status: {r1.status_code}")
    # Get
    r2 = c.get("/trace/d1")
    print(f"Get Status: {r2.status_code}")
    print(f"Body: {r2.json()}")
