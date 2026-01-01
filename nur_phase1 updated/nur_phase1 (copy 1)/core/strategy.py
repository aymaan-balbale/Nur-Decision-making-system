#!/usr/bin/env python3
"""
Nur Trading Strategy - 200 EMA Crossover with Candle-Close Logic

Implements the exact 200 EMA crossover strategy:
- BUY when candle closes above EMA200 AND previous candle closed below/touching
- SELL when candle closes below EMA200 AND previous candle closed above/touching
- Candle-close only (no repainting)
"""

from typing import Optional, Dict, Any


class TradingStrategy:
    """
    Implements the exact 200 EMA crossover strategy.

    Entry Conditions:
    - BUY: Candle closes above EMA200 AND previous candle was below/touching EMA
    - SELL: Candle closes below EMA200 AND previous candle was above/touching EMA

    No mid-candle trading. No repainting.
    """

    TOUCH_THRESHOLD: float = 0.05  # XAUUSD tolerance

    # =========================
    # BUY CHECK
    # =========================
    @staticmethod
    def check_buy_signal(
        current_candle: Optional[Dict[str, Any]],
        previous_candle: Optional[Dict[str, Any]]
    ) -> bool:
        if current_candle is None or previous_candle is None:
            return False

        if current_candle.get("ema_200") is None or previous_candle.get("ema_200") is None:
            return False

        current_close = current_candle["close"]
        current_ema = current_candle["ema_200"]
        prev_close = previous_candle["close"]
        prev_ema = previous_candle["ema_200"]

        closes_above = current_close > current_ema
        prev_below_or_touching = prev_close <= (prev_ema + TradingStrategy.TOUCH_THRESHOLD)

        buy_signal = closes_above and prev_below_or_touching

        if buy_signal:
            print(
                f"📈 BUY Signal | "
                f"close={current_close:.2f} > ema={current_ema:.2f} | "
                f"prev={prev_close:.2f} <= {prev_ema:.2f}"
            )

        return buy_signal

    # =========================
    # SELL CHECK
    # =========================
    @staticmethod
    def check_sell_signal(
        current_candle: Optional[Dict[str, Any]],
        previous_candle: Optional[Dict[str, Any]]
    ) -> bool:
        if current_candle is None or previous_candle is None:
            return False

        if current_candle.get("ema_200") is None or previous_candle.get("ema_200") is None:
            return False

        current_close = current_candle["close"]
        current_ema = current_candle["ema_200"]
        prev_close = previous_candle["close"]
        prev_ema = previous_candle["ema_200"]

        closes_below = current_close < current_ema
        prev_above_or_touching = prev_close >= (prev_ema - TradingStrategy.TOUCH_THRESHOLD)

        sell_signal = closes_below and prev_above_or_touching

        if sell_signal:
            print(
                f"📉 SELL Signal | "
                f"close={current_close:.2f} < ema={current_ema:.2f} | "
                f"prev={prev_close:.2f} >= {prev_ema:.2f}"
            )

        return sell_signal

    # =========================
    # SIGNAL OUTPUT
    # =========================
    @staticmethod
    def get_signal(
        current_candle: Optional[Dict[str, Any]],
        previous_candle: Optional[Dict[str, Any]]
    ) -> str:
        if TradingStrategy.check_buy_signal(current_candle, previous_candle):
            return "BUY"
        elif TradingStrategy.check_sell_signal(current_candle, previous_candle):
            return "SELL"
        else:
            return "HOLD"

    # =========================
    # EXPLANATION (NO LOGIC CHANGE)
    # =========================
    @staticmethod
    def get_reason(
        current_candle: Optional[Dict[str, Any]],
        previous_candle: Optional[Dict[str, Any]]
    ) -> str:
        """
        Returns human-readable reason for HOLD state.
        Does NOT affect trading logic.
        """
        if current_candle is None or previous_candle is None:
            return "waiting for candle data"

        if current_candle.get("ema_200") is None or previous_candle.get("ema_200") is None:
            return "EMA data not ready"

        curr_close = current_candle["close"]
        curr_ema = current_candle["ema_200"]
        prev_close = previous_candle["close"]
        prev_ema = previous_candle["ema_200"]

        if curr_close > curr_ema:
            if prev_close <= (prev_ema + TradingStrategy.TOUCH_THRESHOLD):
                return "bullish cross forming"
            return "price already above EMA"

        if curr_close < curr_ema:
            if prev_close >= (prev_ema - TradingStrategy.TOUCH_THRESHOLD):
                return "bearish cross forming"
            return "price already below EMA"

        return "price near EMA, waiting"


# =========================
# LOCAL TEST
# =========================
def test_strategy() -> None:
    print("🧪 Testing Strategy Logic")
    print("=" * 50)

    tests = [
        (
            "BUY case",
            {"close": 2050.0, "ema_200": 2049.5},
            {"close": 2049.0, "ema_200": 2049.8},
        ),
        (
            "SELL case",
            {"close": 2049.0, "ema_200": 2049.5},
            {"close": 2050.0, "ema_200": 2049.8},
        ),
        (
            "No signal (already above)",
            {"close": 2050.5, "ema_200": 2049.5},
            {"close": 2050.2, "ema_200": 2049.8},
        ),
        (
            "Touching EMA",
            {"close": 2049.55, "ema_200": 2049.5},
            {"close": 2049.55, "ema_200": 2049.5},
        ),
    ]

    for title, curr, prev in tests:
        print(f"\n{title}")
        signal = TradingStrategy.get_signal(curr, prev)
        reason = TradingStrategy.get_reason(curr, prev)
        print(f"Signal: {signal}")
        print(f"Reason: {reason}")


if __name__ == "__main__":
    test_strategy()
