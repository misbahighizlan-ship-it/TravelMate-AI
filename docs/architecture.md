# Architecture — TravelMate AI

## MVP architecture

```text
Browser dashboard → FastAPI (/api/trips) → Pydantic validation + Correlation ID
  → LangGraph StateGraph: Destination → Budget → Itinerary → Travel information → Supervisor
  → MongoDB Atlas (`travelmate_ai.trip_runs`) → structured response: sections, budget, statuses, logs, incident
```

Each specialist is a LangGraph node and receives the validated request through shared graph state. The supervisor checks statuses and produces a degraded result plus an incident record when a node fails. Each node has at most two attempts. Logs carry the same correlation ID and omit prompts, secrets, and raw exception messages.

## Technology
- Python 3.13+, FastAPI, LangGraph, Pydantic, OpenAI-compatible Python client.
- Ollama Cloud endpoint via environment variables.
- Responsive HTML/CSS/JavaScript dashboard served by FastAPI.
- Pytest + FastAPI TestClient.

## Persistence and access
- MongoDB Atlas stores each run in the `travelmate_ai.trip_runs` collection.
- The connection string is read from `MONGODB_URI`; it must stay in local `.env` and Render secrets, never in source control.
- Use a dedicated MongoDB database user with `readWrite` permission on `travelmate_ai`, not an Atlas project-owner account.
- The run-history endpoint requires a separate admin token. Individual trip responses return only to the request that created them.
- The DB and collection are created automatically by MongoDB on the first saved trip if they do not already exist.

## Honest MVP limits
- Budget categories are a transparent percentage allocation of the user's total, not researched market prices.
- No live weather, route, opening-hour, booking, or availability integration.
- Atlas records persist independently of app restarts; the app still needs an allowed network path from the local computer or Render.
- A successful local test does not mean Render is deployed.
