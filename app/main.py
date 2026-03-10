from fastapi import FastAPI
import csv
import random

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

            score = random.randint(60, 95)

            entry_price = round(random.uniform(50, 500), 2)
            stop_loss = round(entry_price * 0.95, 2)
            target_1 = round(entry_price * 1.10, 2)

            opportunities_list.append({
                "symbol": row["symbol"],
                "company": row["company"],
                "signal": "watch",
                "signal_label_ar": "مراقبة",
                "score": score,
                "risk_level": "medium",
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "target_1": target_1,
                "trend": "uptrend",
                "timeframe": "daily",
                "reason": "تمت قراءة السهم من قائمة الأسهم الشرعية",
                "ai_summary_ar": "هذا السهم مأخوذ من ملف الأسهم الشرعية ويجري تقييمه بواسطة محرك BIGBANG."
            })

    return {"opportunities": opportunities_list}
