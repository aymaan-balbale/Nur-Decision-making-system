#!/usr/bin/env python3
"""
Nur Trading Agent - LIVE EMA200 + DEMO TRADE EXECUTION
"""

import time
from collections import deque
from bridge.bridge import read_market, wait_for_market, send_command


# =========================
# EMA CALCULATOR
# =========================
class EMA200:
    def __init__(self, period=200):
        self.period = period
        self.multiplier = 2 / (period + 1)
        self.ema = None

    def update(self, price):
        if self.ema is None:
            self.ema = price
        else:
            self.ema = (price - self.ema) * self.multiplier + self.ema
        return self.ema


# =========================
# LIVE MODE WITH TRADE EXECUTION
# =========================
def run_live_with_trades():
    print("\n🔴 LIVE MODE — EMA200 + DEMO TRADING ENABLED")
    print("=" * 60)

    wait_for_market()

    ema200 = EMA200()
    price_history = deque(maxlen=2)

    last_time = None
    last_trade = None   # prevents duplicate trades

    print("📡 Listening to MT5 live ticks...\n")

    while True:
        market = read_market()
        if not market:
            time.sleep(0.2)
            continue

        if market["time"] == last_time:
            continue
        last_time = market["time"]

        price = market["bid"]
        ema = ema200.update(price)

        price_history.append(price)

        print(
            f"{market['time']} | "
            f"PRICE={price:.2f} | "
            f"EMA200={ema:.2f}"
        )

        if len(price_history) < 2:
            continue

        prev_price = price_history[0]
        curr_price = price_history[1]

        # =========================
        # EMA200 CROSS LOGIC
        # =========================
        if prev_price < ema and curr_price > ema and last_trade != "BUY":
            print("✅ BUY SIGNAL → SENDING TO MT5\n")

            sl = round(price - 2.0, 2)   # demo SL
            tp = round(price + 4.0, 2)   # demo TP

            send_command("BUY", sl, tp)
            last_trade = "BUY"

        elif prev_price > ema and curr_price < ema and last_trade != "SELL":
            print("❌ SELL SIGNAL → SENDING TO MT5\n")

            sl = round(price + 2.0, 2)   # demo SL
            tp = round(price - 4.0, 2)   # demo TP

            send_command("SELL", sl, tp)
            last_trade = "SELL"

        time.sleep(0.2)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    run_live_with_trades()
