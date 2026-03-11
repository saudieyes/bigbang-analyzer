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
            sma10 = None
            sma20 = None

            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="3mo")

                if not hist.empty:
                    closes = hist["Close"].dropna()

                    if len(closes) > 0:
                        current_price = float(closes.iloc[-1])

                    if len(closes) >= 10:
                        sma10 = float(closes.tail(10).mean())

                    if len(closes) >= 20:
                        sma20 = float(closes.tail(20).mean())

                    if current_price is not None and sma10 is not None:
                        if current_price > sma10:
                            trend = "uptrend"
                        elif current_price < sma10:
                            trend = "downtrend"
                        else:
                            trend = "neutral"

            except:
                current_price = None
                trend = "unknown"
                sma10 = None
                sma20 = None

            score = 50
            signal = "WATCH"
            entry_price = None
            stop_loss = None
            target = None

            if current_price is not None:
                entry_price = round(current_price, 2)
                stop_loss = round(current_price * 0.95, 2)
                target = round(current_price * 1.10, 2)

                if sma10 is not None and sma20 is not None:
                    if current_price > sma10 and current_price > sma20:
                        score = 90
                        signal = "STRONG_BUY"
                    elif current_price > sma10:
                        score = 75
                        signal = "BUY"
                    elif abs(current_price - sma10) / sma10 < 0.01:
                        score = 60
                        signal = "WATCH"
                    else:
                        score = 40
                        signal = "WEAK"

                elif sma10 is not None:
                    if current_price > sma10:
                        score = 75
                        signal = "BUY"
                    else:
                        score = 40
                        signal = "WEAK"

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
