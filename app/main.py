from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.database import init_db, list_runs, save_run
from app.graph import AGENTS, travel_graph

load_dotenv()
app = FastAPI(title="TravelMate AI", version="0.2.0", description="Smart tourism planning MVP with LangGraph supervision and MongoDB Atlas")
INDEX = Path(__file__).parent / "static" / "index.html"

class TripRequest(BaseModel):
    departure_city: str = Field(min_length=2, max_length=80)
    destination: str = Field(min_length=2, max_length=100)
    duration_days: int = Field(ge=1, le=30)
    total_budget: float = Field(gt=0, le=1_000_000)
    travelers: int = Field(ge=1, le=20)
    interests: list[str] = Field(min_length=1, max_length=10)
    accommodation_type: str = Field(min_length=2, max_length=60)
    demo_fail_agent: Literal["destination", "budget", "itinerary", "travel_info"] | None = None

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard():
    return HTMLResponse(INDEX.read_text(encoding="utf-8"))

@app.get("/api/health")
def health():
    configured = bool(os.getenv("OLLAMA_API_KEY") and os.getenv("OLLAMA_API_KEY") != "replace_me_locally")
    return {"status": "ok", "ai_provider": "Ollama Cloud" if configured else "Demo fallback (API key not configured)", "llm_configured": configured}

@app.get("/api/agents")
def agents():
    descriptions = {"destination": "Finds destinations matching interests.", "budget": "Creates a transparent percentage allocation of the requested budget.", "itinerary": "Drafts a manageable day-by-day plan.", "travel_info": "Lists general cautions and clearly flags information not verified live.", "supervisor": "Reviews agent statuses, failures, fallbacks, and the final plan."}
    return [{"id": f"travelmate.{name}", "name": name, "version": "0.2.0", "status": "active", "description": descriptions[name]} for name in AGENTS]

@app.get("/api/runs")
def recent_runs(x_admin_token: str | None = Header(default=None, alias="X-Admin-Token")):
    expected = os.getenv("TRAVELMATE_ADMIN_TOKEN")
    if not expected or x_admin_token != expected:
        raise HTTPException(status_code=403, detail="Admin token required.")
    return list_runs()

@app.post("/api/trips")
def create_trip(payload: TripRequest, x_correlation_id: str | None = Header(default=None, alias="X-Correlation-ID")):
    # Fail before spending model calls if MongoDB is not reachable/configured.
    init_db()
    correlation_id = x_correlation_id or f"REQ-{uuid.uuid4().hex[:12].upper()}"
    initial = {
        "request": payload.model_dump(), "correlation_id": correlation_id,
        "demo_fail_agent": payload.demo_fail_agent,
        "agent_status": {name: "PENDING" for name in AGENTS},
        "logs": [], "errors": [], "agent_durations": {},
    }
    result = travel_graph.invoke(initial)
    record = {
        "correlation_id": correlation_id, "health": result.get("health", "DEGRADED"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "request": payload.model_dump(exclude={"demo_fail_agent"}),
        "agent_status": result.get("agent_status", {}), "agent_durations": result.get("agent_durations", {}),
        "logs": result.get("logs", []), "errors": result.get("errors", []),
        "incident": result.get("incident"), "budget": result.get("budget_result", {}),
        "plan_sections": result.get("plan_sections", {}),
        "final_plan": result.get("final_plan", "No plan generated."),
    }
    # Connection errors are surfaced instead of silently pretending the record was persisted.
    save_run(record)
    return record
