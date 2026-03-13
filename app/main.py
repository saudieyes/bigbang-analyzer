from fastapi import FastAPI, Body
import csv
import yfinance as yf
import time

app = FastAPI()

opportunities_cache = None
cache_time = 0
CACHE_DURATION = 600


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


def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return None

    gains = []
    losses = []

    for i in range(1, len(closes)):
        diff = float(closes.iloc[i] - closes.iloc[i - 1])
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))

    recent_gains = gains[-period:]
    recent_losses = losses[-period:]

    avg_gain = sum(recent_gains) / period
    avg_loss = sum(recent_losses) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)


def calculate_ema(values, period):
    if len(values) < period:
        return None

    multiplier = 2 / (period + 1)
    ema = float(values.iloc[0])

    for i in range(1, len(values)):
        ema = (float(values.iloc[i]) - ema) * multiplier + ema

    return ema


def calculate_macd(closes):
    if len(closes) < 35:
        return None, None

    ema12_list = []
    ema26_list = []

    for i in range(len(closes)):
        sub = closes.iloc[:i + 1]

        ema12 = calculate_ema(sub, 12)
        ema26 = calculate_ema(sub, 26)

        if ema12 is not None and ema26 is not None:
            ema12_list.append(ema12)
            ema26_list.append(ema26)

    if len(ema12_list) == 0 or len(ema26_list) == 0:
        return None, None

    macd_series = []
    min_len = min(len(ema12_list), len(ema26_list))

    for i in range(min_len):
        macd_series.append(ema12_list[i] - ema26_list[i])

    if len(macd_series) < 9:
        return None, None

    signal_line = macd_series[0]
    multiplier = 2 / (9 + 1)

    for i in range(1, len(macd_series)):
        signal_line = (macd_series[i] - signal_line) * multiplier + signal_line

    macd_value = macd_series[-1]

    return round(macd_value, 4), round(signal_line, 4)


def get_stock_data(symbol):
    current_price = None
    trend = "unknown"
    score = 0
    signal = "WEAK"
    entry_price = None
    stop_loss = None
    target = None
    reason = "لم يتم التحليل بعد"
    rsi = None
    volume_ratio = None
    macd_value = None
    macd_signal = None

    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="3mo")

        if hist.empty:
            raise Exception("No history")

        closes = hist["Close"].dropna()
        volumes = hist["Volume"].dropna() if "Volume" in hist.columns else []

        sma10 = None
        sma20 = None
        close_5 = None
        close_10 = None
        avg_volume_20 = None
        latest_volume = None

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

        if len(volumes) >= 20:
            avg_volume_20 = float(volumes.tail(20).mean())
            latest_volume = float(volumes.iloc[-1])

        if latest_volume is not None and avg_volume_20 is not None and avg_volume_20 > 0:
            volume_ratio = latest_volume / avg_volume_20

        rsi = calculate_rsi(closes, 14)
        macd_value, macd_signal = calculate_macd(closes)

        if current_price is not None:
            entry_price = round(current_price, 2)
            stop_loss = round(current_price * 0.95, 2)
            target = round(current_price * 1.10, 2)

        # الاتجاه
        if current_price is not None and sma10 is not None:
            if current_price > sma10:
                trend = "uptrend"
                score += 25
            else:
                trend = "downtrend"
                score += 5

        if current_price is not None and sma20 is not None:
            if current_price > sma20:
                score += 20
            else:
                score += 5

        # الزخم
        if current_price is not None and close_5 is not None:
            if current_price > close_5:
                score += 15
            else:
                score += 5

        if current_price is not None and close_10 is not None:
            if current_price > close_10:
                score += 10
            else:
                score += 5

        # RSI
        if rsi is not None:
            if 45 <= rsi <= 65:
                score += 15
            elif 35 <= rsi < 45 or 65 < rsi <= 72:
                score += 8
            else:
                score += 0

        # الحجم
        if volume_ratio is not None:
            if volume_ratio >= 1.3:
                score += 10
            elif volume_ratio >= 1.0:
                score += 5
            else:
                score += 0

        # MACD
        if macd_value is not None and macd_signal is not None:
            if macd_value > macd_signal and macd_value > 0:
                score += 20
            elif macd_value > macd_signal:
                score += 10
            else:
                score += 0

        if score > 100:
            score = 100

        if score >= 82:
            signal = "STRONG_BUY"
            reason = "اتجاه صاعد وزخم جيد وRSI مناسب وMACD إيجابي مع دعم من حجم التداول"
        elif score >= 68:
            signal = "BUY"
            reason = "السهم جيد للمتابعة والشراء التدريجي مع تأكيد مقبول من المؤشرات"
        elif score >= 52:
            signal = "WATCH"
            reason = "السهم مقبول لكن يحتاج تأكيد أكبر قبل الدخول"
        else:
            signal = "WEAK"
            reason = "السهم لا يملك معطيات فنية كافية الآن"

    except:
        current_price = None
        trend = "unknown"
        score = 0
        signal = "WEAK"
        entry_price = None
        stop_loss = None
        target = None
        reason = "تعذر جلب البيانات من السوق"
        rsi = None
        volume_ratio = None
        macd_value = None
        macd_signal = None

    return {
        "current_price": current_price,
        "trend": trend,
        "score": score,
        "signal": signal,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "target": target,
        "reason": reason,
        "rsi": rsi,
        "volume_ratio": round(volume_ratio, 2) if volume_ratio is not None else None,
        "macd": macd_value,
        "macd_signal": macd_signal
    }


@app.get("/opportunities")
def opportunities():
    global opportunities_cache
    global cache_time

    current_time = time.time()

    if opportunities_cache and (current_time - cache_time < CACHE_DURATION):
        return {"opportunities": opportunities_cache}

    opportunities_list = []

    with open("shariah_stocks.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            symbol = row.get("Symbol", "").strip()
            company = row.get("Company Name", "").strip()

            if symbol == "":
                continue

            data = get_stock_data(symbol)

            opportunities_list.append({
                "symbol": symbol,
                "company": company,
                "current_price": data["current_price"],
                "trend": data["trend"],
                "score": data["score"],
                "signal": data["signal"],
                "entry_price": data["entry_price"],
                "stop_loss": data["stop_loss"],
                "target": data["target"],
                "reason": data["reason"],
                "rsi": data["rsi"],
                "volume_ratio": data["volume_ratio"],
                "macd": data["macd"],
                "macd_signal": data["macd_signal"]
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

    opportunities_cache = opportunities_list
    cache_time = current_time

    return {"opportunities": opportunities_list}


@app.get("/opportunities-simple")
def opportunities_simple():
    data = opportunities()

    lines = []

    for item in data["opportunities"]:
        symbol = item["symbol"]
        signal = item["signal"]

        if signal == "STRONG_BUY":
            signal_ar = "شراء قوي"
        elif signal == "BUY":
            signal_ar = "شراء"
        elif signal == "WATCH":
            signal_ar = "مراقبة"
        else:
            signal_ar = "ضعيف"

        lines.append(f"{symbol} - {signal_ar}")

    return {"lines": lines}


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

            closes = hist["Close"].dropna() if not hist.empty else []

            current_price = None

            if len(closes) > 0:
                current_price = float(closes.iloc[-1])

            if current_price is None:
                try:
                    current_price = float(stock.fast_info["lastPrice"])
                except:
                    current_price = None

            sma10 = None
            close_5 = None

            if len(closes) >= 10:
                sma10 = float(closes.tail(10).mean())

            if len(closes) > 5:
                close_5 = float(closes.iloc[-6])

            if current_price is not None and sma10 is not None:
                trend = "uptrend" if current_price > sma10 else "downtrend"
            else:
                trend = "unknown"

            if current_price is not None:
                profit_percent = ((current_price - buy_price) / buy_price) * 100
            else:
                profit_percent = None

            momentum = "unknown"
            if current_price is not None and close_5 is not None:
                momentum = "positive" if current_price > close_5 else "negative"

            rsi = calculate_rsi(closes, 14)

            signal = "HOLD"
            reason = ""

            if trend == "uptrend" and momentum == "positive" and profit_percent is not None and profit_percent < 5:
                signal = "ADD"
                reason = "الاتجاه صاعد والزخم إيجابي والسهم قريب من سعر الشراء"

            elif trend == "uptrend" and profit_percent is not None and profit_percent >= 5:
                signal = "HOLD"
                reason = "السهم في اتجاه صاعد والربح جيد"

            elif trend == "downtrend" and profit_percent is not None and profit_percent > 5:
                signal = "REDUCE"
                reason = "السهم بدأ يضعف بعد ربح جيد"

            elif trend == "downtrend" and profit_percent is not None and profit_percent < -5:
                signal = "EXIT"
                reason = "السهم في اتجاه هابط والخسارة تتزايد"

            elif current_price is None:
                signal = "HOLD"
                reason = "تعذر جلب السعر الحالي"

            stop_loss = None
            target = None

            if current_price is not None:
                stop_loss = round(current_price * 0.95, 2)
                target = round(current_price * 1.12, 2)

        except:
            current_price = None
            profit_percent = None
            trend = "unknown"
            signal = "HOLD"
            reason = "تعذر جلب بيانات السهم"
            rsi = None
            stop_loss = None
            target = None

        results.append({
            "symbol": symbol,
            "quantity": quantity,
            "buy_price": buy_price,
            "current_price": current_price,
            "profit_percent": profit_percent,
            "trend": trend,
            "signal": signal,
            "reason": reason,
            "rsi": rsi,
            "stop_loss": stop_loss,
            "target": target
        })

    return {"portfolio": results}


@app.get("/portfolio-test")
def portfolio_test():
    sample_stocks = [
        {"symbol": "AAPL", "buy_price": 220, "quantity": 10},
        {"symbol": "MSFT", "buy_price": 350, "quantity": 5},
        {"symbol": "NVDA", "buy_price": 120, "quantity": 4}
    ]

    return portfolio_analysis(sample_stocks)
