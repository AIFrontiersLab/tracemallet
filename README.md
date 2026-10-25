# Tracemallet

Provide immediate, visual debugging of LLM execution traces to identify latency spikes and cost anomalies.

# TraceIngest MVP

A minimal FastAPI service to ingest and retrieve trace data.

## Usage

### Ingest
POST /ingest
{
  "trace_id": "string",
  "spans": [{"name": "string", "latency_ms": number}]
}

### Get Trace
GET /trace/{trace_id}

## Run

uvicorn main:app --reload

## Test

pytest -q