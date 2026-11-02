# Agent Cards — v0.2.0

**Owner:** TravelMate project team (student project)  
**Last reviewed:** 2026-11-02

## Shared contract

- **Input:** validated trip request (`departure_city`, `destination`, `duration_days`, `total_budget`, `travelers`, `interests`, `accommodation_type`) and `correlation_id`.
- **Demo-only input:** `demo_fail_agent` can simulate a failure for classroom testing.
- **Output:** each node returns its result, status, duration, and structured log events.
- **Communication:** LangGraph shared state; no agent-to-agent HTTP calls.
- **Common monitoring:** correlation ID, agent status, duration, errors, and retry events are logged.
- **Retry policy:** two attempts total (one retry), then a fallback where available.
- **KPI limitation:** output quality, recommendation accuracy, and user satisfaction are not automatically measured.

## Destination Discovery — `travelmate.destination`

- **Objective:** suggest up to three areas that match the request and explain why.
- **Authorized tools:** Ollama Cloud chat completion only; no browsing or search tools.
- **Data sources:** user request and configured language model; no live tourism database.
- **Limits:** recommendations and current conditions are not independently verified.
- **KPIs:** status and duration are logged; recommendation quality is not automatically scored.
- **Failure handling:** retry once, then show an explicit fallback and record the failure.
- **Status:** implemented.

## Budget Management — `travelmate.budget`

- **Objective:** divide the requested total into transport, accommodation, food, activities, and contingency.
- **Authorized tools:** deterministic Python calculation; no external pricing tools or model call.
- **Data sources:** user-provided total budget only.
- **Limits:** allocations are planning assumptions, not researched prices or quotes.
- **KPIs:** allocation total is checked by a unit test; status and duration are logged.
- **Failure handling:** retry once, then show budget unavailable and record an incident.
- **Status:** implemented.

## Itinerary Planning — `travelmate.itinerary`

- **Objective:** draft a day-by-day itinerary using the request and earlier agent results.
- **Authorized tools:** Ollama Cloud chat completion only; no maps or route-planning tools.
- **Data sources:** user request, destination result, and budget allocation.
- **Limits:** travel times, opening hours, and activity availability are not verified.
- **KPIs:** status and duration are logged; itinerary realism is not automatically scored.
- **Failure handling:** retry once, then show an explicit fallback and record the failure.
- **Status:** implemented.

## Travel Information — `travelmate.travel_info`

- **Objective:** provide general planning cautions and identify facts that need checking.
- **Authorized tools:** Ollama Cloud chat completion only; no browsing or live-data tools.
- **Data sources:** user request and configured language model.
- **Limits:** weather, transport status, opening hours, and availability are not live-verified.
- **KPIs:** status and duration are logged; live-source coverage is not available.
- **Failure handling:** retry once, then show a warning to verify current official sources.
- **Status:** implemented.

## Supervisor & Monitoring — `travelmate.supervisor`

- **Objective:** review node statuses, assemble the response, and mark workflow health.
- **Authorized tools:** LangGraph shared state and structured logs; no external tools.
- **Data sources:** agent results, statuses, errors, durations, and correlation ID.
- **Limits:** review is rule-based; no automatic human notification or content-accuracy scoring.
- **KPIs:** reports `HEALTHY` or `DEGRADED`; records an incident when a specialist fails.
- **Failure handling:** exposes the fallback and incident in the response.
- **Status:** implemented.

**Version:** SemVer `0.2.0` — MVP; review before release.