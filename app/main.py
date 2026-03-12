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


def get_stock_data(symbol):

    current_price = None
    trend = "unknown"
    score = 0
    signal = "WEAK"
    entry_price = None
    stop_loss = None
    target = None
    reason = ""

    try:

        stock = yf.Ticker(symbol)
        hist = stock.history(period="3mo")

        closes = hist["Close"].dropna() if not hist.empty else []

        sma10 = None
        sma20 = None
        close_5 = None
        close_10 = None

        if len(closes) > 0:
            current_price = float(closes.iloc[-1])

        if current_price is None:
            try:
                current_price = float(stock.fast_info["lastPrice"])
            except:
                current_price = None

        if len(closes) >= 10:
            sma10 = float(closes.tail(10).mean())
            close_5 = float(closes.iloc[-6])

        if len(closes) >= 20:
            sma20 = float(closes.tail(20).mean())
            close_10 = float(closes.iloc[-11])

        if current_price is not None:
            entry_price = round(current_price, 2)
            stop_loss = round(current_price * 0.95, 2)
            target = round(current_price * 1.10, 2)

        if current_price and sma10:
            if current_price > sma10:
                trend = "uptrend"
                score += 30
            else:
                trend = "downtrend"

        if current_price and sma20:
            if current_price > sma20:
                score += 25

        if current_price and close_5:
            if current_price > close_5:
                score += 20

        if current_price and close_10:
            if current_price > close_10:
                score += 15

        if score >= 85:
            signal = "STRONG_BUY"
            reason = "الاتجاه صاعد والزخم قوي"
        elif score >= 70:
            signal = "BUY"
            reason = "زخم إيجابي"
        elif score >= 55:
            signal = "WATCH"
            reason = "سهم للمراقبة"
        else:
            signal = "WEAK"
            reason = "ضعيف حالياً"

    except:
        reason = "تعذر تحليل السهم"

    return {
        "current_price": current_price,
        "trend": trend,
        "score": score,
        "signal": signal,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "target": target,
        "reason": reason
    }


@app.get("/opportunities")
def opportunities():

    opportunities_list = []

    with open("shariah_stocks.csv", "r", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:

            symbol = row["symbol"]
            company = row["company"]

            data = get_stock_data(symbol)

            opportunities_list.append({
                "symbol": symbol,
                "company": company,
                "price": data["current_price"],
                "signal": data["signal"],
                "score": data["score"]
            })

    opportunities_list = sorted(
        opportunities_list,
        key=lambda x: x["score"],
        reverse=True
    )

    opportunities_list = [
        item for item in opportunities_list
        if item["signal"] in ["STRONG_BUY", "BUY", "WATCH"]
    ]

    opportunities_list = opportunities_list[:10]

    return {"opportunities": opportunities_list}


@app.get("/opportunities-simple")
def opportunities_simple():

    data = opportunities()

    lines = []

    for item in data["opportunities"]:

        symbol = item["symbol"]
        signal = item["signal"]

        lines.append(f"{symbol} - {signal}")

    return {"lines": lines}
