from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from openai import OpenAI
from typing_extensions import TypedDict

load_dotenv()
AGENTS = ("destination", "budget", "itinerary", "travel_info", "supervisor")

class TravelState(TypedDict, total=False):
    request: dict[str, Any]
    correlation_id: str
    demo_fail_agent: str | None
    agent_status: dict[str, str]
    logs: list[dict[str, Any]]
    errors: list[dict[str, Any]]
    agent_durations: dict[str, int]
    destination_result: str
    budget_result: dict[str, Any]
    itinerary_result: str
    travel_info_result: str
    final_plan: str
    health: str
    incident: dict[str, Any] | None
    plan_sections: dict[str, Any]

def _log(state: TravelState, agent: str, event: str, status: str, duration_ms: int = 0, error_code: str | None = None) -> dict[str, Any]:
    row = {
        "correlation_id": state["correlation_id"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent, "event": event, "status": status,
        "duration_ms": duration_ms,
    }
    if error_code:
        row["error_code"] = error_code  # Never log prompts, API keys, or raw exceptions.
    return row

def ollama_chat(system_prompt: str, user_prompt: str) -> str:
    key = os.getenv("OLLAMA_API_KEY")
    if not key or key == "replace_me_locally":
        raise RuntimeError("AI key is not configured")
    client = OpenAI(
        api_key=key,
        base_url=os.getenv("OLLAMA_BASE_URL", "https://ollama.com/v1"),
        timeout=45.0,
    )
    response = client.chat.completions.create(
        model=os.getenv("OLLAMA_MODEL", "gemma4:31b"),
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        temperature=0.3,
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Empty model response")
    return content.strip()

def _run_agent(state: TravelState, name: str, output_key: str, action, fallback):
    statuses = dict(state.get("agent_status", {}))
    logs = list(state.get("logs", []))
    errors = list(state.get("errors", []))
    statuses[name] = "RUNNING"
    logs.append(_log(state, name, "started", "RUNNING"))
    result = None
    error_code = None
    total_start = time.perf_counter()
    for attempt in (1, 2):  # One bounded retry.
        start = time.perf_counter()
        try:
            if state.get("demo_fail_agent") == name:
                raise RuntimeError("Simulated failure for classroom demonstration")
            result = action()
            elapsed = int((time.perf_counter() - start) * 1000)
            logs.append(_log(state, name, "completed", "SUCCESS", elapsed))
            statuses[name] = "SUCCESS"
            break
        except Exception as exc:
            elapsed = int((time.perf_counter() - start) * 1000)
            error_code = "SimulatedFailure" if state.get("demo_fail_agent") == name else type(exc).__name__
            logs.append(_log(state, name, "retry" if attempt == 1 else "failed", "FAILED", elapsed, error_code))
            if attempt == 2:
                statuses[name] = "FAILED"
                errors.append({"agent": name, "error_code": error_code, "attempts": 2, "severity": "medium"})
                result = fallback
    total_ms = int((time.perf_counter() - total_start) * 1000)
    return {output_key: result, "agent_status": statuses, "logs": logs, "errors": errors, "agent_durations": {**state.get("agent_durations", {}), name: total_ms}}

def destination_node(state: TravelState):
    r = state["request"]
    prompt = f"Trip request: departure={r['departure_city']}; destination/region={r['destination']}; days={r['duration_days']}; interests={', '.join(r['interests'])}; travelers={r['travelers']}. Recommend at most 3 fitting areas. Give one short reason for each. Plain text, no Markdown, max 120 words. Do not claim real-time facts or availability."
    return _run_agent(state, "destination", "destination_result", lambda: ollama_chat("You are the Destination Discovery Agent. Return concise plain text only.", prompt), "AI unavailable: verify local attractions from current official sources.")

def budget_split(total: float) -> dict[str, Any]:
    # Transparent planning allocation only; not a market-price estimate.
    shares = [("Transport", .25), ("Accommodation", .35), ("Food", .20), ("Activities", .15)]
    allocations = {name: round(total * share, 2) for name, share in shares}
    allocations["Contingency"] = round(total - sum(allocations.values()), 2)
    return {"currency": "MAD", "total": round(total, 2), "allocations": allocations, "note": "Planning split only; prices are not live quotes. Confirm actual costs before travel."}

def budget_node(state: TravelState):
    return _run_agent(state, "budget", "budget_result", lambda: budget_split(float(state["request"]["total_budget"])), {"currency": "MAD", "total": state["request"]["total_budget"], "allocations": {}, "note": "Budget calculation unavailable; verify manually."})

def itinerary_node(state: TravelState):
    r = state["request"]
    prompt = f"Create a realistic {r['duration_days']}-day draft itinerary for {r['destination']} from {r['departure_city']} for {r['travelers']} traveler(s). Interests: {', '.join(r['interests'])}. Accommodation preference: {r['accommodation_type']}. Give one short line per day, at most 3 activities each; plain text, no Markdown, max 350 words. Group nearby activities; mark travel times as estimates. Do not invent bookings, live prices, opening hours, or availability. Discovery suggestions: {state.get('destination_result','')} Budget allocation: {state.get('budget_result',{}).get('allocations',{})} MAD."
    return _run_agent(state, "itinerary", "itinerary_result", lambda: ollama_chat("You are the Itinerary Planning Agent. Create a concise readable draft, not a reservation.", prompt), "AI unavailable: verify travel times and opening hours before building an itinerary.")

def travel_info_node(state: TravelState):
    r = state["request"]
    prompt = f"For a draft trip to {r['destination']} lasting {r['duration_days']} days, give at most 5 concise general planning cautions in plain text, no Markdown. No browsing or live data is connected. Explicitly say weather, opening hours, transport status, and availability are not verified."
    def action():
        text = ollama_chat("You are the Travel Information Agent. Never present simulated or general knowledge as real-time verified information.", prompt)
        return text + "\n\nLive verification: none connected. Check official current sources for weather, opening hours, transport, and restrictions."
    return _run_agent(state, "travel_info", "travel_info_result", action, "No live information source is connected. Verify weather, opening hours, transport, and restrictions using current official sources.")

def supervisor_node(state: TravelState):
    started = time.perf_counter()
    statuses = dict(state.get("agent_status", {}))
    statuses["supervisor"] = "RUNNING"
    logs = list(state.get("logs", []))
    logs.append(_log(state, "supervisor", "review_started", "RUNNING"))
    failed = [name for name in AGENTS if name != "supervisor" and statuses.get(name) != "SUCCESS"]
    health = "DEGRADED" if failed else "HEALTHY"
    r = state["request"]
    b = state.get("budget_result", {})
    allocations = b.get("allocations", {})
    plan_sections = {
        "destination": state.get("destination_result", "Non disponible"),
        "budget_note": b.get("note", "Estimation indicative."),
        "itinerary": state.get("itinerary_result", "Non disponible"),
        "travel_info": state.get("travel_info_result", "Non disponible"),
    }
    plan = (
        f"## Votre projet de voyage\n\n**Destination demandée :** {r['destination']}  \n**Départ :** {r['departure_city']} · **Durée :** {r['duration_days']} jours · **Voyageurs :** {r['travelers']}\n\n"
        f"### Découverte\n{state.get('destination_result','Non disponible')}\n\n"
        f"### Budget indicatif — {b.get('total', r['total_budget']):,.2f} MAD\n" +
        "\n".join(f"- {k}: {v:,.2f} MAD" for k, v in allocations.items()) +
        f"\n\n_{b.get('note','Estimation indicative.')}_\n\n"
        f"### Itinéraire proposé\n{state.get('itinerary_result','Non disponible')}\n\n"
        f"### Informations à vérifier\n{state.get('travel_info_result','Non disponible')}\n\n"
        "**À retenir :** Il s'agit d'une proposition, pas d'une réservation ni d'une garantie de prix ou de disponibilité."
    )
    incident = None
    if failed:
        incident = {"severity": "medium", "status": "open", "failed_agents": failed, "attempts": 2, "action": "Fallback affiché; intervention humaine recommandée."}
    statuses["supervisor"] = "SUCCESS"
    elapsed = int((time.perf_counter() - started) * 1000)
    logs.append(_log(state, "supervisor", "review_completed", "SUCCESS", elapsed))
    durations = dict(state.get("agent_durations", {})); durations["supervisor"] = elapsed
    return {"final_plan": plan, "plan_sections": plan_sections, "health": health, "incident": incident, "agent_status": statuses, "logs": logs, "agent_durations": durations}

def build_graph():
    builder = StateGraph(TravelState)
    builder.add_node("destination", destination_node)
    builder.add_node("budget", budget_node)
    builder.add_node("itinerary", itinerary_node)
    builder.add_node("travel_info", travel_info_node)
    builder.add_node("supervisor", supervisor_node)
    builder.add_edge(START, "destination")
    builder.add_edge("destination", "budget")
    builder.add_edge("budget", "itinerary")
    builder.add_edge("itinerary", "travel_info")
    builder.add_edge("travel_info", "supervisor")
    builder.add_edge("supervisor", END)
    return builder.compile()

travel_graph = build_graph()
