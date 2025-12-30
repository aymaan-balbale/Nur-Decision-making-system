import time
import os
from datetime import datetime
from collections import deque

# ===== PATHS =====
MARKET_FILE = r"C:\Users\Abusahil\AppData\Roaming\MetaQuotes\Terminal\Common\Files\market.csv"
COMMANDS_FILE = r"C:\Users\Abusahil\AppData\Roaming\MetaQuotes\Terminal\Common\Files\commands.csv"

# ===== EMA CONFIG =====
EMA_PERIOD = 200
alpha = 2 / (EMA_PERIOD + 1)

ema = None
current_minute = None
minute_prices = []

prev_close = None
prev_ema = None
prev_high = None
prev_low = None

last_seen = ""

# Swing storage
recent_highs = deque(maxlen=5)
recent_lows = deque(maxlen=5)

def parse_line(line):
    parts = line.split()
    ts = datetime.strptime(parts[0] + " " + parts[1], "%Y.%m.%d %H:%M:%S")
    bid = float(parts[-2])
    ask = float(parts[-1])
    return ts, (bid + ask) / 2

def write_command(action, sl, tp):
    with open(COMMANDS_FILE, "w") as f:
        f.write(f"{action},XAUUSD,{sl:.2f},{tp:.2f}")
    print(f"📤 COMMAND SENT → {action} | SL={sl:.2f} TP={tp:.2f}")

print("EMA200 Engine Started (M1 Candle Close)")
print("Waiting for data...\n")

while True:
    try:
        if not os.path.exists(MARKET_FILE):
            time.sleep(0.5)
            continue

        with open(MARKET_FILE, "r", encoding="utf-16") as f:
            data = f.read().strip()

        if not data or data == last_seen:
            time.sleep(0.5)
            continue

        last_seen = data
        ts, price = parse_line(data)

        minute = ts.replace(second=0)

        # ===== NEW CANDLE =====
        if current_minute and minute != current_minute:
            close_price = minute_prices[-1]
            high_price = max(minute_prices)
            low_price = min(minute_prices)

            # EMA UPDATE
            if ema is None:
                ema = close_price
            else:
                ema = alpha * close_price + (1 - alpha) * ema

            print(f"[{current_minute}] CLOSE={close_price:.2f} EMA200={ema:.2f}")

            recent_highs.append(high_price)
            recent_lows.append(low_price)

            # ===== ENTRY + COMMAND =====
            if prev_close is not None and prev_ema is not None:

                # BUY
                if close_price > ema and prev_close <= prev_ema:
                    sl = prev_low
                    tp = max(recent_highs)
                    print("✅ CONFIRMED BUY SETUP")
                    write_command("BUY", sl, tp)

                # SELL
                elif close_price < ema and prev_close >= prev_ema:
                    sl = prev_high
                    tp = min(recent_lows)
                    print("✅ CONFIRMED SELL SETUP")
                    write_command("SELL", sl, tp)

            prev_close = close_price
            prev_ema = ema
            prev_high = high_price
            prev_low = low_price

            minute_prices.clear()

        current_minute = minute
        minute_prices.append(price)

        time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nStopped")
        break
