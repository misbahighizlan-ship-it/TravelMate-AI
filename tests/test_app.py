from fastapi.testclient import TestClient
from app import database
from app.main import app
import pytest

client = TestClient(app)
PAYLOAD = {
    "departure_city": "Casablanca", "destination": "Maroc", "duration_days": 7,
    "total_budget": 6000, "travelers": 1, "interests": ["nature", "culture"],
    "accommodation_type": "Maison d’hôtes"
}

def fake_model(system_prompt, user_prompt):
    return "Proposition de démonstration; vérifiez les détails avec des sources actuelles."

class FakeCursor:
    def __init__(self, records):
        self.records = records

    def sort(self, key, direction):
        self.records.sort(key=lambda row: row.get(key, ""), reverse=direction == -1)
        return self

    def limit(self, count):
        self.records = self.records[:count]
        return self

    def __iter__(self):
        return iter(self.records)

class FakeCollection:
    def __init__(self):
        self.records = {}

    def create_index(self, _keys):
        return "created_at_-1"

    def replace_one(self, selector, document, upsert=False):
        self.records[selector["correlation_id"]] = dict(document)

    def find(self, _query, projection):
        rows = [dict(row) for row in self.records.values()]
        if projection and projection.get("_id") == 0:
            for row in rows:
                row.pop("_id", None)
        return FakeCursor(rows)

@pytest.fixture(autouse=True)
def isolated_database(monkeypatch):
    collection = FakeCollection()
    monkeypatch.setattr(database, "_get_collection", lambda: collection)

def test_health_endpoint():
    assert client.get("/api/health").status_code == 200

def test_invalid_duration_is_rejected():
    response = client.post("/api/trips", json={**PAYLOAD, "duration_days": 0})
    assert response.status_code == 422

def test_budget_split_sums_to_total():
    from app.graph import budget_split
    result = budget_split(6000)
    assert round(sum(result["allocations"].values()), 2) == 6000
    assert result["note"].startswith("Planning split")

def test_workflow_propagates_correlation_id(monkeypatch):
    monkeypatch.setattr("app.graph.ollama_chat", fake_model)
    response = client.post("/api/trips", headers={"X-Correlation-ID": "REQ-TEST-1"}, json=PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert data["correlation_id"] == "REQ-TEST-1"
    assert all(log["correlation_id"] == "REQ-TEST-1" for log in data["logs"])
    assert all(status == "SUCCESS" for status in data["agent_status"].values())

def test_budget_agent_incident_is_detected(monkeypatch):
    monkeypatch.setattr("app.graph.ollama_chat", fake_model)
    response = client.post("/api/trips", json={**PAYLOAD, "demo_fail_agent": "budget"})
    data = response.json()
    assert data["health"] == "DEGRADED"
    assert data["agent_status"]["budget"] == "FAILED"
    assert data["incident"]["failed_agents"] == ["budget"]

def test_run_is_saved_in_local_database(monkeypatch):
    monkeypatch.setattr("app.graph.ollama_chat", fake_model)
    response = client.post("/api/trips", json=PAYLOAD)
    assert response.status_code == 200
    saved = database.list_runs()
    assert len(saved) == 1
    assert saved[0]["correlation_id"] == response.json()["correlation_id"]

def test_run_history_requires_admin_token():
    assert client.get("/api/runs").status_code == 403

def test_recent_runs_are_returned(monkeypatch):
    monkeypatch.setenv("TRAVELMATE_ADMIN_TOKEN", "test-token")
    monkeypatch.setattr("app.graph.ollama_chat", fake_model)
    client.post("/api/trips", json=PAYLOAD)
    response = client.get("/api/runs", headers={"X-Admin-Token": "test-token"})
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_dashboard_and_openapi():
    assert client.get("/").status_code == 200
    assert client.get("/docs").status_code == 200
