from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {
        "name": "BIGBANG Analyzer",
        "tagline": "Where opportunities explode",
        "status": "engine running"
    }

@app.get("/health")
def health():
    return {"status": "BIGBANG engine running"}

@app.get("/opportunities")
def opportunities():
    return {
        "opportunities": [
            {"symbol": "NVDA", "signal": "watch"},
            {"symbol": "ANET", "signal": "watch"},
            {"symbol": "NVO", "signal": "watch"},
            {"symbol": "CRM", "signal": "watch"},
            {"symbol": "HAL", "signal": "watch"}
        ]
    }
