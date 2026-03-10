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
            {
                "symbol": "NVDA",
                "signal": "watch",
                "score": 88,
                "entry_price": 131.8,
                "stop_loss": 125.9,
                "target_1": 139.0,
                "trend": "uptrend",
                "timeframe": "daily",
                "reason": "اختراق مقاومة مع زخم قوي"
            },
            {
                "symbol": "ANET",
                "signal": "watch",
                "score": 84,
                "entry_price": 312.5,
                "stop_loss": 299.8,
                "target_1": 325.0,
                "trend": "uptrend",
                "timeframe": "daily",
                "reason": "اتجاه صاعد وإعادة اختبار ناجحة"
            },
            {
                "symbol": "NVO",
                "signal": "watch",
                "score": 79,
                "entry_price": 96.4,
                "stop_loss": 91.2,
                "target_1": 102.0,
                "trend": "uptrend",
                "timeframe": "daily",
                "reason": "ارتداد من دعم مع تحسن الزخم"
            },
            {
                "symbol": "CRM",
                "signal": "watch",
                "score": 76,
                "entry_price": 284.0,
                "stop_loss": 272.5,
                "target_1": 296.0,
                "trend": "neutral",
                "timeframe": "daily",
                "reason": "تماسك إيجابي وقرب من نقطة دخول"
            },
            {
                "symbol": "HAL",
                "signal": "watch",
                "score": 72,
                "entry_price": 34.8,
                "stop_loss": 32.9,
                "target_1": 37.5,
                "trend": "uptrend",
                "timeframe": "daily",
                "reason": "فوق المتوسطات مع هدف قريب واضح"
            }
        ]
    }
