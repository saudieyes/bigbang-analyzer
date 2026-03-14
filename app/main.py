from fastapi import FastAPI, Body, Query
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


# -----------------------------------
# مؤشرات فنية
# -----------------------------------

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


# -----------------------------------
# منطق الفرص
# -----------------------------------

def is_true_bigbang(
    signal,
    trend,
    rsi,
    macd_value,
    macd_signal,
    volume_ratio,
    entry_status,
    breakout_ready,
    breakout_score
):
    if signal != "STRONG_BUY":
        return False

    if trend != "uptrend":
        return False

    if breakout_ready != "HIGH" or breakout_score < 80:
        return False

    if entry_status != "IN_ZONE":
        return False

    if rsi is None or not (48 <= rsi <= 65):
        return False

    if macd_value is None or macd_signal is None:
        return False

    if not (macd_value > macd_signal and macd_value > 0):
        return False

    if volume_ratio is None or volume_ratio < 1.0:
        return False

    return True


def get_opportunity_type(
    signal,
    trend,
    breakout_ready,
    breakout_score,
    rsi,
    entry_status,
    macd_value,
    macd_signal,
    volume_ratio
):
    if is_true_bigbang(
        signal,
        trend,
        rsi,
        macd_value,
        macd_signal,
        volume_ratio,
        entry_status,
        breakout_ready,
        breakout_score
    ):
        return "BIGBANG"

    if signal in ["STRONG_BUY", "BUY"] and trend == "uptrend":
        return "GROWTH"

    return "WATCH"


def opportunity_sort_key(item):
    priority = 0

    if item["opportunity_type"] == "BIGBANG":
        priority = 4
    elif item["opportunity_type"] == "GROWTH" and item["entry_status"] == "IN_ZONE":
        priority = 3
    elif item["opportunity_type"] == "GROWTH" and item["entry_status"] == "ABOVE_ZONE":
        priority = 2
    elif item["signal"] == "WATCH":
        priority = 1

    return (
        priority,
        item.get("breakout_score", 0),
        item.get("score", 0),
        1 if item.get("entry_status") == "IN_ZONE" else 0
    )


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

    entry_low = None
    entry_high = None
    entry_status = "unknown"
    breakout_ready = "LOW"
    breakout_score = 0
    opportunity_type = "WATCH"

    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="3mo")

        if hist.empty:
            raise Exception("No history")

        closes = hist["Close"].dropna()
        highs = hist["High"].dropna() if "High" in hist.columns else closes
        lows = hist["Low"].dropna() if "Low" in hist.columns else closes
        volumes = hist["Volume"].dropna() if "Volume" in hist.columns else []

        sma10 = None
        sma20 = None
        close_5 = None
        close_10 = None
        avg_volume_20 = None
        latest_volume = None
        high_20 = None
        low_20 = None
        range_percent_20 = None
        near_high_percent = None

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
            high_20 = float(highs.tail(20).max())
            low_20 = float(lows.tail(20).min())

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

        if sma10 is not None:
            entry_low = round(sma10 * 0.99, 2)
            entry_high = round(sma10 * 1.01, 2)

            if current_price is not None:
                if current_price < entry_low:
                    entry_status = "BELOW_ZONE"
                elif current_price > entry_high:
                    entry_status = "ABOVE_ZONE"
                else:
                    entry_status = "IN_ZONE"

        if current_price is not None and high_20 is not None and low_20 is not None and current_price > 0:
            range_percent_20 = ((high_20 - low_20) / current_price) * 100.0
            near_high_percent = ((high_20 - current_price) / current_price) * 100.0

            if range_percent_20 <= 8:
                breakout_score += 35
            elif range_percent_20 <= 12:
                breakout_score += 20

            if near_high_percent <= 2.5:
                breakout_score += 35
            elif near_high_percent <= 5:
                breakout_score += 20

            if volume_ratio is not None:
                if volume_ratio >= 1.2:
                    breakout_score += 20
                elif volume_ratio >= 1.0:
                    breakout_score += 10

            if macd_value is not None and macd_signal is not None and macd_value > macd_signal:
                breakout_score += 10

            if breakout_score >= 80:
                breakout_ready = "HIGH"
            elif breakout_score >= 60:
                breakout_ready = "MEDIUM"
            else:
                breakout_ready = "LOW"

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

        if rsi is not None:
            if 45 <= rsi <= 65:
                score += 15
            elif 35 <= rsi < 45 or 65 < rsi <= 72:
                score += 8
            else:
                score += 0

        if volume_ratio is not None:
            if volume_ratio >= 1.3:
                score += 10
            elif volume_ratio >= 1.0:
                score += 5
            else:
                score += 0

        if macd_value is not None and macd_signal is not None:
            if macd_value > macd_signal and macd_value > 0:
                score += 20
            elif macd_value > macd_signal:
                score += 10
            else:
                score += 0

        if entry_status == "IN_ZONE":
            score += 5

        if breakout_ready == "HIGH":
            score += 5

        if score > 100:
            score = 100

        if score >= 84:
            signal = "STRONG_BUY"
            reason = "اتجاه صاعد وزخم جيد وRSI مناسب وMACD إيجابي مع دعم من حجم التداول"
        elif score >= 70:
            signal = "BUY"
            reason = "السهم جيد للمتابعة والشراء التدريجي مع تأكيد مقبول من المؤشرات"
        elif score >= 55:
            signal = "WATCH"
            reason = "السهم مقبول لكن يحتاج تأكيد أكبر قبل الدخول"
        else:
            signal = "WEAK"
            reason = "السهم لا يملك معطيات فنية كافية الآن"

        extra_notes = []

        if entry_status == "IN_ZONE":
            extra_notes.append("السهم داخل منطقة دخول جيدة")
        elif entry_status == "ABOVE_ZONE":
            extra_notes.append("السهم مرتفع قليلاً عن منطقة الدخول")
        elif entry_status == "BELOW_ZONE":
            extra_notes.append("السهم أسفل منطقة الدخول ويحتاج تأكيد ارتداد")

        if breakout_ready == "HIGH":
            extra_notes.append("جاهزية الاختراق عالية")
        elif breakout_ready == "MEDIUM":
            extra_notes.append("جاهزية الاختراق متوسطة")

        if len(extra_notes) > 0:
            reason = reason + " - " + " - ".join(extra_notes)

        opportunity_type = get_opportunity_type(
            signal,
            trend,
            breakout_ready,
            breakout_score,
            rsi,
            entry_status,
            macd_value,
            macd_signal,
            volume_ratio
        )

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
        entry_low = None
        entry_high = None
        entry_status = "unknown"
        breakout_ready = "LOW"
        breakout_score = 0
        opportunity_type = "WATCH"

    return {
        "symbol": symbol,
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
        "macd_signal": macd_signal,
        "entry_low": entry_low,
        "entry_high": entry_high,
        "entry_status": entry_status,
        "breakout_ready": breakout_ready,
        "breakout_score": breakout_score,
        "opportunity_type": opportunity_type
    }


def build_opportunities_response(refresh=0):
    global opportunities_cache
    global cache_time

    current_time = time.time()

    if refresh != 1 and opportunities_cache and (current_time - cache_time < CACHE_DURATION):
        return opportunities_cache

    opportunities_list = []

    with open("shariah_stocks.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            symbol = row.get("Symbol", "").strip()

            if symbol == "":
                continue

            data = get_stock_data(symbol)

            if data is not None:
                opportunities_list.append(data)

    opportunities_list = [
        item for item in opportunities_list
        if item["signal"] in ["STRONG_BUY", "BUY", "WATCH"]
    ]

    opportunities_list = sorted(
        opportunities_list,
        key=opportunity_sort_key,
        reverse=True
    )

    top_opportunity = opportunities_list[0] if len(opportunities_list) > 0 else None

    bigbang_opportunity = None
    for item in opportunities_list:
        if item["opportunity_type"] == "BIGBANG":
            bigbang_opportunity = item
            break

    response = {
        "bigbang_opportunity": bigbang_opportunity,
        "top_opportunity": top_opportunity,
        "rotation_suggestion": None,
        "opportunities": opportunities_list[:10]
    }

    opportunities_cache = response
    cache_time = current_time

    return response


@app.get("/opportunities")
def opportunities(refresh: int = Query(0)):
    return build_opportunities_response(refresh)


@app.get("/opportunities-simple")
def opportunities_simple():
    data = build_opportunities_response(0)

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


# -----------------------------------
# منطق المحفظة
# -----------------------------------

def calculate_portfolio_confidence(trend, momentum, rsi, macd_value, macd_signal, profit_percent):
    confidence = 0

    if trend == "uptrend":
        confidence += 30
    elif trend == "downtrend":
        confidence += 5

    if momentum == "positive":
        confidence += 20
    elif momentum == "negative":
        confidence += 5

    if rsi is not None:
        if 45 <= rsi <= 65:
            confidence += 20
        elif 35 <= rsi < 45 or 65 < rsi <= 72:
            confidence += 10

    if macd_value is not None and macd_signal is not None:
        if macd_value > macd_signal and macd_value > 0:
            confidence += 20
        elif macd_value > macd_signal:
            confidence += 10

    if profit_percent is not None:
        if profit_percent >= 20:
            confidence += 10
        elif profit_percent >= 5:
            confidence += 7
        elif profit_percent >= 0:
            confidence += 5

    if confidence > 100:
        confidence = 100

    return confidence


def calculate_risk_level(rsi, trend):
    if rsi is None:
        return "MEDIUM"

    if rsi > 75:
        return "HIGH"

    if 65 <= rsi <= 75:
        return "MEDIUM"

    if rsi < 35 and trend == "downtrend":
        return "HIGH"

    if rsi < 40 and trend == "downtrend":
        return "MEDIUM"

    return "LOW"


def portfolio_signal_and_reason(trend, momentum, profit_percent, current_price):
    signal = "HOLD"
    reason = ""

    if trend == "uptrend" and momentum == "positive" and profit_percent is not None and profit_percent < 15:
        signal = "ADD"
        reason = "الاتجاه صاعد والزخم إيجابي والربح ما زال في بدايته"

    elif trend == "uptrend" and momentum == "positive" and profit_percent is not None and profit_percent >= 15:
        signal = "HOLD"
        reason = "السهم قوي والربح جيد ويمكن الاستمرار بالاحتفاظ"

    elif trend == "uptrend" and momentum == "negative" and profit_percent is not None and profit_percent >= 15:
        signal = "REDUCE"
        reason = "الربح جيد لكن الزخم بدأ يضعف، يفضل تخفيف جزء من الكمية"

    elif trend == "downtrend" and profit_percent is not None and profit_percent > 5:
        signal = "REDUCE"
        reason = "السهم بدأ يضعف بعد ربح جيد"

    elif trend == "downtrend" and profit_percent is not None and profit_percent < -5:
        signal = "EXIT"
        reason = "السهم في اتجاه هابط والخسارة تتزايد"

    elif current_price is None:
        signal = "HOLD"
        reason = "تعذر جلب السعر الحالي"

    if reason == "":
        if trend == "uptrend":
            reason = "السهم ما زال متماسكًا لكن لا توجد إشارة قوية لزيادة الكمية الآن"
        elif trend == "downtrend":
            reason = "السهم يمر بمرحلة ضعف لكن لم يعطِ إشارة خروج واضحة بعد"
        else:
            reason = "البيانات الحالية غير كافية لاتخاذ قرار أقوى من الاحتفاظ"

    return signal, reason


def rank_portfolio_item(item):
    signal_score = 0

    if item["signal"] == "ADD":
        signal_score = 4
    elif item["signal"] == "HOLD":
        signal_score = 3
    elif item["signal"] == "REDUCE":
        signal_score = 2
    elif item["signal"] == "EXIT":
        signal_score = 1

    risk_bonus = 0
    if item["risk_level"] == "LOW":
        risk_bonus = 2
    elif item["risk_level"] == "MEDIUM":
        risk_bonus = 1

    return (signal_score * 100) + item["confidence"] + risk_bonus


def make_rotation_suggestion(worst_position, bigbang_opportunity):
    if bigbang_opportunity is None:
        return "لا توجد فرصة BIGBANG حقيقية الآن، احتفظ بتوزيع محفظتك الحالي"

    if worst_position is None:
        return None

    worst_symbol = worst_position.get("symbol", "")
    bigbang_symbol = bigbang_opportunity.get("symbol", "")

    if worst_symbol == "" or bigbang_symbol == "":
        return None

    if worst_symbol == bigbang_symbol:
        return "أفضل فرصة اليوم موجودة أصلًا داخل محفظتك"

    worst_signal = worst_position.get("signal", "HOLD")
    worst_confidence = worst_position.get("confidence", 0)

    if worst_signal in ["REDUCE", "EXIT"] or worst_confidence <= 50:
        return f"تقليل {worst_symbol} وتحويل جزء من السيولة إلى {bigbang_symbol}"

    return f"راقب {bigbang_symbol} كفرصة قوية، ولا توجد ضرورة حالياً لتغيير مكونات المحفظة"


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

            if hist.empty:
                raise Exception("No history")

            closes = hist["Close"].dropna()
            volumes = hist["Volume"].dropna() if "Volume" in hist.columns else []

            current_price = None
            if len(closes) > 0:
                current_price = float(closes.iloc[-1])

            if current_price is None:
                try:
                    current_price = float(stock.fast_info["lastPrice"])
                except:
                    current_price = None

            sma10 = None
            sma20 = None
            close_5 = None
            macd_value = None
            macd_signal = None

            if len(closes) >= 10:
                sma10 = float(closes.tail(10).mean())
                close_5 = float(closes.iloc[-6])

            if len(closes) >= 20:
                sma20 = float(closes.tail(20).mean())

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
            macd_value, macd_signal = calculate_macd(closes)

            confidence = calculate_portfolio_confidence(
                trend,
                momentum,
                rsi,
                macd_value,
                macd_signal,
                profit_percent
            )

            risk_level = calculate_risk_level(rsi, trend)

            signal, reason = portfolio_signal_and_reason(
                trend,
                momentum,
                profit_percent,
                current_price
            )

            stop_loss = None
            target = None
            add_zone_low = None
            add_zone_high = None

            if current_price is not None:
                stop_loss = round(current_price * 0.95, 2)
                target = round(current_price * 1.12, 2)

            if sma20 is not None:
                add_zone_low = round(sma20 * 0.99, 2)
                add_zone_high = round(sma20 * 1.01, 2)

        except:
            current_price = None
            profit_percent = None
            trend = "unknown"
            signal = "HOLD"
            reason = "تعذر جلب بيانات السهم"
            rsi = None
            stop_loss = None
            target = None
            confidence = 0
            risk_level = "MEDIUM"
            momentum = "unknown"
            add_zone_low = None
            add_zone_high = None
            macd_value = None
            macd_signal = None

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
            "target": target,
            "confidence": confidence,
            "risk_level": risk_level,
            "momentum": momentum,
            "add_zone_low": add_zone_low,
            "add_zone_high": add_zone_high,
            "macd": macd_value,
            "macd_signal": macd_signal
        })

    best_position = None
    worst_position = None

    if len(results) > 0:
        best_position = sorted(results, key=rank_portfolio_item, reverse=True)[0]
        worst_position = sorted(results, key=rank_portfolio_item)[0]

    opportunities_data = build_opportunities_response(0)
    bigbang_opportunity = opportunities_data.get("bigbang_opportunity")

    rotation_suggestion = make_rotation_suggestion(worst_position, bigbang_opportunity)

    return {
        "best_position": best_position,
        "worst_position": worst_position,
        "bigbang_opportunity": bigbang_opportunity,
        "rotation_suggestion": rotation_suggestion,
        "portfolio": results
    }


@app.get("/portfolio-test")
def portfolio_test():
    sample_stocks = [
        {"symbol": "AAPL", "buy_price": 220, "quantity": 10},
        {"symbol": "MSFT", "buy_price": 350, "quantity": 5},
        {"symbol": "NVDA", "buy_price": 120, "quantity": 4}
    ]

    return portfolio_analysis(sample_stocks)
