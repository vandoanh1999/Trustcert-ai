from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_score():
    data = {"age_days": 200, "verified_ratio": 0.8, "activity_30d": 0.7, "reports_90d": 0.05}
    r = client.post("/score", json=data)
    assert r.status_code == 200
    assert "score" in r.json()
    assert "bucket" in r.json()