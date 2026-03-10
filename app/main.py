from fastapi import FastAPI
import csv
import yfinance as yf

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

            symbol = row["symbol"]
            company = row["company"]

            try:
                stock = yf.Ticker(symbol)
                price = stock.history(period="1d")["Close"].iloc[-1]
            except:
                price = None

            opportunities_list.append({
                "symbol": symbol,
                "company": company,
                "current_price": price,
                "signal": "watch",
                "signal_label_ar": "مراقبة",
                "trend": "unknown",
                "reason": "تم جلب السعر الحقيقي من السوق"
            })

    return {"opportunities": opportunities_list}
