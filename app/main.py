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

            except:
                current_price = None
                trend = "unknown"

            score = 50
            signal = "WATCH"
            entry_price = None
            stop_loss = None
            target = None

            if current_price is not None:

                if trend == "uptrend":
                    score = 80
                    signal = "BUY"

                elif trend == "downtrend":
                    score = 40
                    signal = "WEAK"

                else:
                    score = 60
                    signal = "WATCH"

                entry_price = round(current_price, 2)
                stop_loss = round(current_price * 0.95, 2)
                target = round(current_price * 1.10, 2)

            opportunities_list.append({
                "symbol": symbol,
                "company": company,
                "current_price": current_price,
                "trend": trend,
                "score": score,
                "signal": signal,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "target": target
            })

    return {"opportunities": opportunities_list}
