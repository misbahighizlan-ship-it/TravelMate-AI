# Changelog

## 0.2.0 — MongoDB Atlas
- Replaced local SQLite persistence with MongoDB Atlas in `travelmate_ai.trip_runs`.
- Added environment-based connection configuration and Render secret mapping.
- Updated tests to use an isolated fake collection; no live Atlas credentials are needed for tests.

## 0.1.0 — MVP starter
- LangGraph workflow with four specialist nodes and a supervisor.
- FastAPI endpoints, correlation IDs, execution logs, bounded retries, and incident simulation.
- Responsive French dashboard, tests, Dockerfile, and deployment notes.
- Travel costs are planning allocations, not live market quotes; no booking or live availability.
