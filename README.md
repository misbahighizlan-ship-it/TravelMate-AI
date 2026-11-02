# TravelMate AI — Smart Tourism MVP

A beginner-friendly, observable travel-planning MVP using LangGraph, FastAPI, Ollama Cloud, and a responsive dashboard.

## What works in this MVP
- Validated trip request and REST API (`POST /api/trips`).
- LangGraph workflow with Destination, Budget, Itinerary, Travel Information, and Supervisor nodes.
- Correlation ID propagation, statuses, duration, structured logs, one bounded retry, and incident simulation.
- MongoDB Atlas persistence for runs in `travelmate_ai.trip_runs`; history access requires an admin token.
- Responsive dashboard at `/`; OpenAPI/Swagger at `/docs`.
- Pytest suite.

## Important limits
Budget is a planning allocation of the user's total, not a researched fare quote. No live weather, opening hours, travel status, bookings, or availability. Use only as a planning draft. MongoDB Atlas must be configured with a database user restricted to `readWrite` on `travelmate_ai`; never commit the connection string.

## Windows 11 setup
1. In VS Code open this folder and use PowerShell terminal. Python is invoked as `py`.
2. Create/activate the environment if needed:
   ```powershell
   py -m venv .venv
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
4. In Atlas, create a database user with `readWrite` access only to `travelmate_ai`, and allow your current IP under Network Access for local testing.
5. Edit your local `.env` (keep your existing Ollama key) and set `MONGODB_URI` to your private Atlas connection string. Keep `MONGODB_DATABASE=travelmate_ai` and `MONGODB_COLLECTION=trip_runs`. Never commit or share `.env`.
6. Run:
   ```powershell
   uvicorn app.main:app --reload
   ```
7. Open `http://127.0.0.1:8000`; API docs: `http://127.0.0.1:8000/docs`.
8. Test:
   ```powershell
   pytest -q
   ```

If there is no Ollama key or the cloud call fails, agents use explicit fallbacks and the run is marked DEGRADED. A MongoDB connection is required to save trip runs. Tests mock both the model and database and do not need live credentials.

## Docker
Build with `docker build -t travelmate-ai .` and run with `docker run --rm -p 8000:8000 --env-file .env travelmate-ai`.

## GitHub Actions / Render
CI runs Pytest on pushes and pull requests. `render.yaml` is a deployment blueprint; a public deployment still requires connecting a repository, setting `OLLAMA_API_KEY` and `MONGODB_URI` as secrets, allowing the Render service to connect to Atlas, deploying, and verifying the URL.
