"""
EMA200 Trading Engine - Real-time EMA200 crossover strategy for MT5.

This module monitors MT5 market data file and generates BUY/SELL signals
based on price crossing the 200-period Exponential Moving Average.
"""

import time
import os
from datetime import datetime
from collections import deque
from typing import Tuple, Optional, List

# ===== PATHS =====
MARKET_FILE = r"C:\Users\Abusahil\AppData\Roaming\MetaQuotes\Terminal\Common\Files\market.csv"
COMMANDS_FILE = r"C:\Users\Abusahil\AppData\Roaming\MetaQuotes\Terminal\Common\Files\commands.csv"

# ===== EMA CONFIG =====
EMA_PERIOD: int = 200
alpha: float = 2 / (EMA_PERIOD + 1)

# Global state variables
ema: Optional[float] = None
current_minute: Optional[datetime] = None
minute_prices: List[float] = []

prev_close: Optional[float] = None
prev_ema: Optional[float] = None
prev_high: Optional[float] = None
prev_low: Optional[float] = None

last_seen: str = ""

# Swing storage for recent highs and lows (used for TP calculation)
recent_highs: deque = deque(maxlen=5)
recent_lows: deque = deque(maxlen=5)


def parse_line(line: str) -> Tuple[datetime, float]:
    """
    Parse a line from the MT5 market data file.
    
    Args:
        line: Raw line from market.csv file
        
    Returns:
        Tuple of (timestamp, mid_price)
    """
    parts = line.split()
    ts = datetime.strptime(parts[0] + " " + parts[1], "%Y.%m.%d %H:%M:%S")
    bid = float(parts[-2])
    ask = float(parts[-1])
    return ts, (bid + ask) / 2


def write_command(action: str, sl: float, tp: float) -> None:
    """
    Write trading command to MT5 commands file.
    
    Args:
        action: Trading action ("BUY" or "SELL")
        sl: Stop loss price
        tp: Take profit price
    """
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

                # BUY Signal: Price crosses above EMA200
                if close_price > ema and prev_close <= prev_ema:
                    sl = prev_low
                    tp = max(recent_highs)
                    print("✅ CONFIRMED BUY SETUP")
                    write_command("BUY", sl, tp)

                # SELL Signal: Price crosses below EMA200
                elif close_price < ema and prev_close >= prev_ema:
                    sl = prev_high
                    tp = min(recent_lows)
                    print("✅ CONFIRMED SELL SETUP")
                    write_command("SELL", sl, tp)

            # Store previous candle values for next comparison
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
