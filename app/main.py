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

            current_price = None
            trend = "unknown"

            try:
                stock = yf.Ticker(symbol)

                hist_1d = stock.history(period="1mo")

                if not hist_1d.empty:
                    current_price = float(hist_1d["Close"].iloc[-1])

                    if len(hist_1d["Close"]) >= 20:
                        sma20 = float(hist_1d["Close"].tail(20).mean())

                        if current_price > sma20:
                            trend = "uptrend"
                        elif current_price < sma20:
                            trend = "downtrend"
                        else:
                            trend = "neutral"
                    else:
                        trend = "unknown"

            except:
                current_price = None
                trend = "unknown"

            opportunities_list.append({
                "symbol": symbol,
                "company": company,
                "current_price": current_price,
                "signal": "watch",
                "signal_label_ar": "مراقبة",
                "trend": trend,
                "reason": "تم جلب السعر الحقيقي وتحديد الاتجاه بشكل أولي من السوق"
            })

    return {"opportunities": opportunities_list}
