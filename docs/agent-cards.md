# Agent Cards — v0.2.0

Shared input: validated trip request (`departure_city`, `destination`, `duration_days`, `total_budget`, `travelers`, `interests`, `accommodation_type`) plus `correlation_id`. Shared output: named result, status (`PENDING/RUNNING/SUCCESS/FAILED`), duration and structured log events. Protocol: LangGraph shared state; no agent-to-agent HTTP calls. Owner: TravelMate project team (student project).

| Agent / ID | Responsibilities and output | Dependencies / limits | Error handling / status |
|---|---|---|---|
| Destination Discovery / `travelmate.destination` | Suggests up to three suitable areas and explains interest fit. Output: text recommendation. | Ollama Cloud model; no live search. | Two attempts, then explicit fallback; status logged. Active in code. |
| Budget Management / `travelmate.budget` | Allocates user total across transport, accommodation, food, activities, contingency. Output: MAD breakdown. | Deterministic arithmetic; percentages are planning assumptions, not quotes. | Two attempts; failure recorded and incident raised. Active in code. |
| Itinerary Planning / `travelmate.itinerary` | Drafts day-by-day schedule and asks model to group nearby activities. Output: itinerary text. | Depends on discovery and budget outputs; travel time is unverified. | Two attempts, then fallback; status logged. Active in code. |
| Travel Information / `travelmate.travel_info` | Gives general planning cautions and labels live facts unverified. Output: caution text. | Ollama Cloud; no connected real-time source. | Two attempts, then fallback; status logged. Active in code. |
| Supervisor & Monitoring / `travelmate.supervisor` | Reviews all node statuses, combines results, exposes incidents/health. | LangGraph shared state and logs. | Degraded health on failed node; fallback is visible. Active in code. |

Input schema and API response are defined in `app/main.py`; graph state is defined in `app/graph.py`. Version: SemVer `0.2.0` (MVP; subject to test and review).
