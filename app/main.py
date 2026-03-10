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
                hist = stock.history(period="3mo")

                if not hist.empty:
                    closes = hist["Close"].dropna()

                    if len(closes) > 0:
                        current_price = float(closes.iloc[-1])

                    if len(closes) >= 10 and current_price is not None:
                        sma10 = float(closes.tail(10).mean())

                        if current_price > sma10:
                            trend = "uptrend"
                        elif current_price < sma10:
                            trend = "downtrend"
                        else:
                            trend = "neutral"

                if current_price is None:
                    try:
                        current_price = float(stock.fast_info["lastPrice"])
                    except:
                        current_price = None

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
                "reason": "تم جلب السعر الحقيقي وتحديد الاتجاه الأولي بناءً على متوسط 10 أيام"
            })

    return {"opportunities": opportunities_list}
