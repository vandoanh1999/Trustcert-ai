from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="TrustCert AI", version="1.0")

class Features(BaseModel):
    age_days: float
    verified_ratio: float
    activity_30d: float
    reports_90d: float

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/score")
def compute_score(f: Features):
    # Thuật toán cơ bản
    score = (
        0.25 * (f.age_days / 365) +
        0.35 * f.verified_ratio +
        0.30 * f.activity_30d -
        0.20 * f.reports_90d
    )
    score = max(0, min(1, score))
    bucket = (
        "A" if score >= 0.85 else
        "B" if score >= 0.65 else
        "C" if score >= 0.4 else "D"
    )
    return {"score": round(score, 3), "bucket": bucket}