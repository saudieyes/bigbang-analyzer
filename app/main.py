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

from fastapi import Body

@app.post("/portfolio-analysis")
def portfolio_analysis(stocks: list = Body(...)):

    results = []

    for item in stocks:

        symbol = item["symbol"]
        buy_price = item["buy_price"]
        quantity = item["quantity"]

        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="3mo")

            closes = hist["Close"].dropna()
            current_price = float(closes.iloc[-1])

            sma10 = float(closes.tail(10).mean())

            profit_percent = ((current_price - buy_price) / buy_price) * 100

            trend = "uptrend" if current_price > sma10 else "downtrend"

            signal = "HOLD"

            if trend == "uptrend" and profit_percent > 10:
                signal = "HOLD"

            elif trend == "uptrend" and profit_percent < 5:
                signal = "ADD"

            elif trend == "downtrend" and profit_percent > 10:
                signal = "REDUCE"

            elif trend == "downtrend" and profit_percent < -5:
                signal = "EXIT"

        except:
            current_price = None
            profit_percent = None
            trend = "unknown"
            signal = "HOLD"

        results.append({
            "symbol": symbol,
            "quantity": quantity,
            "buy_price": buy_price,
            "current_price": current_price,
            "profit_percent": profit_percent,
            "trend": trend,
            "signal": signal
        })

    return {"portfolio": results}
    @app.get("/portfolio-test")
def portfolio_test():
    sample_stocks = [
        {"symbol": "AAPL", "buy_price": 220, "quantity": 10},
        {"symbol": "MSFT", "buy_price": 350, "quantity": 5},
        {"symbol": "NVDA", "buy_price": 120, "quantity": 4}
    ]

    results = []

    for item in sample_stocks:

        symbol = item["symbol"]
        buy_price = item["buy_price"]
        quantity = item["quantity"]

        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="3mo")

            closes = hist["Close"].dropna()
            current_price = float(closes.iloc[-1])

            sma10 = float(closes.tail(10).mean())

            profit_percent = ((current_price - buy_price) / buy_price) * 100

            trend = "uptrend" if current_price > sma10 else "downtrend"

            signal = "HOLD"

            if trend == "uptrend" and profit_percent > 10:
                signal = "HOLD"

            elif trend == "uptrend" and profit_percent < 5:
                signal = "ADD"

            elif trend == "downtrend" and profit_percent > 10:
                signal = "REDUCE"

            elif trend == "downtrend" and profit_percent < -5:
                signal = "EXIT"

        except:
            current_price = None
            profit_percent = None
            trend = "unknown"
            signal = "HOLD"

        results.append({
            "symbol": symbol,
            "quantity": quantity,
            "buy_price": buy_price,
            "current_price": current_price,
            "profit_percent": profit_percent,
            "trend": trend,
            "signal": signal
        })

    return {"portfolio": results}
