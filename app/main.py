from fastapi import FastAPI, Body
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
            score = 0
            signal = "WEAK"
            entry_price = None
            stop_loss = None
            target = None
            reason = "لم يتم التحليل بعد"

            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="3mo")

                if not hist.empty:
                    closes = hist["Close"].dropna()

                    if len(closes) > 0:
                        current_price = float(closes.iloc[-1])
                        entry_price = round(current_price, 2)
                        stop_loss = round(current_price * 0.95, 2)
                        target = round(current_price * 1.10, 2)

                    sma10 = None
                    sma20 = None
                    close_5 = None
                    close_10 = None

                    if len(closes) >= 10:
                        sma10 = float(closes.tail(10).mean())
                        close_5 = float(closes.iloc[-6])

                    if len(closes) >= 20:
                        sma20 = float(closes.tail(20).mean())
                        close_10 = float(closes.iloc[-11])

                    if current_price is not None and sma10 is not None:
                        if current_price > sma10:
                            trend = "uptrend"
                            score += 30
                        elif current_price < sma10:
                            trend = "downtrend"
                            score += 5
                        else:
                            trend = "neutral"
                            score += 15

                    if current_price is not None and sma20 is not None:
                        if current_price > sma20:
                            score += 25
                        else:
                            score += 5

                    if current_price is not None and close_5 is not None:
                        if current_price > close_5:
                            score += 20
                        else:
                            score += 5

                    if current_price is not None and close_10 is not None:
                        if current_price > close_10:
                            score += 15
                        else:
                            score += 5

                    if score > 100:
                        score = 100

                    if score >= 85:
                        signal = "STRONG_BUY"
                        reason = "الاتجاه صاعد والزخم قوي والسعر فوق المتوسطات"
                    elif score >= 70:
                        signal = "BUY"
                        reason = "الاتجاه جيد والزخم إيجابي"
                    elif score >= 55:
                        signal = "WATCH"
                        reason = "السهم مقبول لكنه يحتاج متابعة"
                    else:
                        signal = "WEAK"
                        reason = "الزخم أو الاتجاه غير كافيين"

            except:
                current_price = None
                trend = "unknown"
                score = 0
                signal = "WEAK"
                entry_price = None
                stop_loss = None
                target = None
                reason = "تعذر جلب البيانات من السوق"

            opportunities_list.append({
                "symbol": symbol,
                "company": company,
                "current_price": current_price,
                "trend": trend,
                "score": score,
                "signal": signal,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "target": target,
                "reason": reason
            })

    opportunities_list = sorted(
        opportunities_list,
        key=lambda x: x["score"],
        reverse=True
    )

    opportunities_list = [
        item for item in opportunities_list
        if item["signal"] in ["STRONG_BUY", "BUY"]
    ]

    opportunities_list = opportunities_list[:10]

    return {"opportunities": opportunities_list}


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
