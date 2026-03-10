from fastapi import FastAPI
import csv

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

    opportunities_list = []

    with open("shariah_stocks.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            opportunities_list.append({
                "symbol": row["symbol"],
                "company": row["company"],
                "signal": "watch",
                "signal_label_ar": "مراقبة",
                "score": 70,
                "risk_level": "medium",
                "entry_price": 100.0,
                "stop_loss": 95.0,
                "target_1": 110.0,
                "trend": "uptrend",
                "timeframe": "daily",
                "reason": "تمت قراءة السهم من قائمة الأسهم الشرعية",
                "ai_summary_ar": "هذا السهم مأخوذ من ملف الأسهم الشرعية وسيتم تحليله لاحقًا بواسطة محرك BIGBANG."
            })

    return {"opportunities": opportunities_list}
