#!/usr/bin/env python3
import sys
print("PYTHON EXECUTABLE:", sys.executable)
print("PYTHON VERSION:", sys.version)

import time
from collections import deque
from typing import Optional, Dict, Any

from bridge.bridge import (
    read_market,
    wait_for_market,
    send_command,
    read_trade_exit,   # 🔹 ADDED
)


STATE_WAITING = "WAITING"
STATE_IN_TRADE = "IN_TRADE"


class EMA200:
    def __init__(self, period: int = 200) -> None:
        self.multiplier = 2 / (period + 1)
        self.ema: Optional[float] = None

    def update(self, price: float) -> float:
        if self.ema is None:
            self.ema = price
        else:
            self.ema = (price - self.ema) * self.multiplier + self.ema
        return self.ema


def run_live_with_trades() -> None:
    print("\n🔴 LIVE MODE — EMA200 + DEMO TRADING ENABLED")
    print("=" * 60)

    wait_for_market()

    ema200 = EMA200()
    price_history: deque = deque(maxlen=2)

    last_time: Optional[str] = None
    last_trade: Optional[str] = None
    last_ticket: Optional[str] = None   # 🔹 ADDED
    state: str = STATE_WAITING

    print("📡 Listening to MT5 live ticks...\n")

    while True:
        # =========================
        # CHECK TRADE EXIT (PHASE 2)
        # =========================
        exit_info = read_trade_exit(last_ticket)
        if exit_info and state == STATE_IN_TRADE:
            print(f"🏁 EXIT → {exit_info['result']}")
            print("🔄 STATE RESET → WAITING\n")

            state = STATE_WAITING
            last_trade = None
            last_ticket = None

        market: Optional[Dict[str, Any]] = read_market()
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
            f"EMA200={ema:.2f} | "
            f"STATE={state}"
        )

        if len(price_history) < 2:
            continue

        prev_price, curr_price = price_history

        if state == STATE_IN_TRADE:
            print("⏸ NO TRADE → already in trade\n")
            time.sleep(0.2)
            continue

        # =========================
        # ENTRY LOGIC (UNCHANGED)
        # =========================
        if prev_price < ema and curr_price > ema and last_trade != "BUY":
            print("✅ BUY SIGNAL → EMA200 bullish cross → SENDING TO MT5\n")

            sl = round(price - 2.0, 2)
            tp = round(price + 4.0, 2)

            last_ticket = send_command("BUY", sl, tp)
            last_trade = "BUY"
            state = STATE_IN_TRADE

        elif prev_price > ema and curr_price < ema and last_trade != "SELL":
            print("❌ SELL SIGNAL → EMA200 bearish cross → SENDING TO MT5\n")

            sl = round(price + 2.0, 2)
            tp = round(price - 4.0, 2)

            last_ticket = send_command("SELL", sl, tp)
            last_trade = "SELL"
            state = STATE_IN_TRADE

        else:
            if curr_price > ema:
                print("ℹ️ NO TRADE → price above EMA, no cross\n")
            elif curr_price < ema:
                print("ℹ️ NO TRADE → price below EMA, no cross\n")
            else:
                print("ℹ️ NO TRADE → price near EMA, waiting\n")

        time.sleep(0.2)


if __name__ == "__main__":
    run_live_with_trades()
