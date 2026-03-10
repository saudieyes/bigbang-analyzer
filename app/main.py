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
                "signal_label_ar": "مراقبة",
                "score": 88,
                "risk_level": "medium",
                "entry_price": 131.8,
                "stop_loss": 125.9,
                "target_1": 139.0,
                "trend": "uptrend",
                "timeframe": "daily",
                "reason": "اختراق مقاومة مع زخم قوي",
                "ai_summary_ar": "السهم في اتجاه صاعد ويظهر زخمًا جيدًا بعد اختراق مقاومة مهمة."
            },
            {
                "symbol": "ANET",
                "signal": "watch",
                "signal_label_ar": "مراقبة",
                "score": 84,
                "risk_level": "medium",
                "entry_price": 312.5,
                "stop_loss": 299.8,
                "target_1": 325.0,
                "trend": "uptrend",
                "timeframe": "daily",
                "reason": "اتجاه صاعد وإعادة اختبار ناجحة",
                "ai_summary_ar": "السهم يحافظ على اتجاه صاعد مع إعادة اختبار جيدة تدعم احتمال استمرار الحركة."
            },
            {
                "symbol": "NVO",
                "signal": "watch",
                "signal_label_ar": "مراقبة",
                "score": 79,
                "risk_level": "medium",
                "entry_price": 96.4,
                "stop_loss": 91.2,
                "target_1": 102.0,
                "trend": "uptrend",
                "timeframe": "daily",
                "reason": "ارتداد من دعم مع تحسن الزخم",
                "ai_summary_ar": "السهم ارتد من منطقة دعم مهمة مع تحسن واضح في الزخم الفني."
            },
            {
                "symbol": "CRM",
                "signal": "watch",
                "signal_label_ar": "مراقبة",
                "score": 76,
                "risk_level": "medium",
                "entry_price": 284.0,
                "stop_loss": 272.5,
                "target_1": 296.0,
                "trend": "neutral",
                "timeframe": "daily",
                "reason": "تماسك إيجابي وقرب من نقطة دخول",
                "ai_summary_ar": "السهم في مرحلة تماسك إيجابي ويقترب من منطقة دخول مناسبة لكن يحتاج متابعة."
            },
            {
                "symbol": "HAL",
                "signal": "watch",
                "signal_label_ar": "مراقبة",
                "score": 72,
                "risk_level": "medium",
                "entry_price": 34.8,
                "stop_loss": 32.9,
                "target_1": 37.5,
                "trend": "uptrend",
                "timeframe": "daily",
                "reason": "فوق المتوسطات مع هدف قريب واضح",
                "ai_summary_ar": "السهم فوق المتوسطات الرئيسية ويملك هدفًا قريبًا واضحًا مع مخاطرة متوسطة."
            }
        ]
    }
