#!/usr/bin/env python3
"""
Nur Trading Agent - LIVE EMA200 + DEMO TRADE EXECUTION

This module implements the live trading system that reads market data from MT5
and executes trades based on EMA200 crossover signals.
"""

import time
from collections import deque
from typing import Optional, Dict, Any
from bridge.bridge import read_market, wait_for_market, send_command


# =========================
# EMA CALCULATOR
# =========================
class EMA200:
    """
    Exponential Moving Average calculator with 200-period.
    
    Uses the standard EMA formula:
    EMA = (Price - Previous EMA) * Multiplier + Previous EMA
    where Multiplier = 2 / (Period + 1)
    """
    
    def __init__(self, period: int = 200) -> None:
        """
        Initialize EMA calculator.
        
        Args:
            period: EMA period (default: 200)
        """
        self.period: int = period
        self.multiplier: float = 2 / (period + 1)
        self.ema: Optional[float] = None

    def update(self, price: float) -> float:
        """
        Update EMA with new price.
        
        Args:
            price: Current price
            
        Returns:
            Updated EMA value
        """
        if self.ema is None:
            self.ema = price
        else:
            self.ema = (price - self.ema) * self.multiplier + self.ema
        return self.ema


# =========================
# LIVE MODE WITH TRADE EXECUTION
# =========================
def run_live_with_trades() -> None:
    """
    Run live trading mode with EMA200 strategy and demo trade execution.
    
    Monitors MT5 market feed, calculates EMA200, and sends trade commands
    when crossover signals are detected.
    """
    print("\n🔴 LIVE MODE — EMA200 + DEMO TRADING ENABLED")
    print("=" * 60)

    wait_for_market()

    ema200 = EMA200()
    price_history: deque = deque(maxlen=2)

    last_time: Optional[str] = None
    last_trade: Optional[str] = None  # Prevents duplicate trades

    print("📡 Listening to MT5 live ticks...\n")

    while True:
        market: Optional[Dict[str, Any]] = read_market()
        if not market:
            time.sleep(0.2)
            continue

        if market["time"] == last_time:
            continue
        last_time = market["time"]

        price: float = market["bid"]
        ema: float = ema200.update(price)

        price_history.append(price)

        print(
            f"{market['time']} | "
            f"PRICE={price:.2f} | "
            f"EMA200={ema:.2f}"
        )

        if len(price_history) < 2:
            continue

        prev_price: float = price_history[0]
        curr_price: float = price_history[1]

        # =========================
        # EMA200 CROSS LOGIC
        # =========================
        # BUY Signal: Price crosses above EMA200
        if prev_price < ema and curr_price > ema and last_trade != "BUY":
            print("✅ BUY SIGNAL → SENDING TO MT5\n")

            sl: float = round(price - 2.0, 2)   # Demo SL
            tp: float = round(price + 4.0, 2)   # Demo TP

            send_command("BUY", sl, tp)
            last_trade = "BUY"

        # SELL Signal: Price crosses below EMA200
        elif prev_price > ema and curr_price < ema and last_trade != "SELL":
            print("❌ SELL SIGNAL → SENDING TO MT5\n")

            sl = round(price + 2.0, 2)   # Demo SL
            tp = round(price - 4.0, 2)   # Demo TP

            send_command("SELL", sl, tp)
            last_trade = "SELL"

        time.sleep(0.2)


# =========================
# RUN
# =========================
if __name__ == "__main__":
    run_live_with_trades()
