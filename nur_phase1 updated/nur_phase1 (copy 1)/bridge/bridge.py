"""
MT5 Bridge Module - File-based communication with MetaTrader 5.

This module provides functions to read market data from and send commands
to MT5 terminal via shared files in the Common Files directory.
"""

import os
import time
from typing import Optional, Dict, Any

# MT5 common files path
MT5_COMMON = os.path.expanduser(
    r"~\AppData\Roaming\MetaQuotes\Terminal\Common\Files"
)

MARKET_FILE: str = os.path.join(MT5_COMMON, "market.csv")
COMMAND_FILE: str = os.path.join(MT5_COMMON, "command.txt")


def wait_for_market() -> None:
    """Wait until MT5 starts writing market data to the market.csv file."""
    print("⏳ Waiting for MT5 market.csv ...")
    while not os.path.exists(MARKET_FILE):
        time.sleep(1)
    print("✅ MT5 market feed detected")


def read_market() -> Optional[Dict[str, Any]]:
    """
    Read latest market tick from MT5 CSV file.
    
    Returns:
        Dictionary with market data (time, symbol, bid, ask) or None if error
    """
    try:
        with open(MARKET_FILE, "r", encoding="utf-16") as f:
            lines = f.readlines()
            if not lines:
                return None

            last = lines[-1].strip().split()
            if len(last) < 4:
                return None

            return {
                "time": last[0] + " " + last[1],
                "symbol": last[2],
                "bid": float(last[3]),
                "ask": float(last[4]) if len(last) > 4 else float(last[3])
            }

    except Exception:
        return None


def send_command(signal: str, sl: float, tp: float) -> None:
    """
    Send trade command to MT5 via command file.
    
    Args:
        signal: Trading signal ("BUY" or "SELL")
        sl: Stop loss price
        tp: Take profit price
    """
    with open(COMMAND_FILE, "w") as f:
        f.write(f"{signal},{sl},{tp}")

    print(f"📤 COMMAND SENT → {signal} | SL={sl} TP={tp}")
