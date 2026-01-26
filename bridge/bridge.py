"""
MT5 Bridge Module - Direct communication with MetaTrader 5 via Python API.

This module provides functions to read market data from and send commands
to MT5 terminal using the official MetaTrader5 Python API.
"""

import os
import time
from datetime import datetime
from typing import Optional, Dict, Any


# =========================
# SAFE MT5 IMPORT
# =========================
try:
    import MetaTrader5 as mt5
    print(f"✅ MetaTrader5 loaded | version={mt5.__version__}")
except Exception as e:
    mt5 = None
    print("❌ MetaTrader5 import failed:", repr(e))


# =========================
# MT5 FILE PATHS
# =========================
MT5_COMMON = os.path.expanduser(
    r"~\AppData\Roaming\MetaQuotes\Terminal\Common\Files"
)

COMMAND_FILE = os.path.join(MT5_COMMON, "command.txt")
TRADES_FILE = os.path.join(MT5_COMMON, "trades.csv")

# Trading symbol
SYMBOL = "XAUUSD"

# MT5 connection state
_mt5_initialized = False


# =========================
# MT5 INITIALIZATION
# =========================
def _initialize_mt5() -> bool:
    """
    Initialize MetaTrader5 connection.
    """
    global _mt5_initialized

    if _mt5_initialized:
        return True

    if mt5 is None:
        print("❌ MetaTrader5 package not available in this Python")
        return False

    if not mt5.initialize():
        print(f"❌ MT5 initialize failed → {mt5.last_error()}")
        return False

    symbol_info = mt5.symbol_info(SYMBOL)
    if symbol_info is None:
        print(f"❌ Symbol {SYMBOL} not found in Market Watch")
        mt5.shutdown()
        return False

    if not symbol_info.visible:
        if not mt5.symbol_select(SYMBOL, True):
            print(f"❌ Failed to select symbol {SYMBOL}")
            mt5.shutdown()
            return False

    _mt5_initialized = True
    return True


# =========================
# WAIT FOR MARKET
# =========================
def wait_for_market() -> None:
    print("⏳ Waiting for MT5 connection...")
    while not _initialize_mt5():
        time.sleep(1)
    print("✅ MT5 connection established")


# =========================
# READ MARKET DATA
# =========================
def read_market() -> Optional[Dict[str, Any]]:
    """
    Read latest market tick from MT5.
    """
    if not _initialize_mt5():
        return None

    tick = mt5.symbol_info_tick(SYMBOL)
    if tick is None:
        return None

    tick_time = datetime.fromtimestamp(tick.time)

    return {
        "time": tick_time.strftime("%Y.%m.%d %H:%M:%S"),
        "symbol": SYMBOL,
        "bid": float(tick.bid),
        "ask": float(tick.ask),
    }


# =========================
# SEND TRADE COMMAND
# =========================
def send_command(action: str, sl: float, tp: float) -> str:
    ticket = str(int(time.time()))

    with open(COMMAND_FILE, "w") as f:
        f.write(f"{ticket},{action},{sl},{tp}")

    print(f"📤 COMMAND SENT → {action} | SL={sl} TP={tp}")
    return ticket


# =========================
# READ TRADE EXIT (PHASE 2)
# =========================
def read_trade_exit(last_ticket: Optional[str]) -> Optional[Dict[str, Any]]:
    if not last_ticket or not os.path.exists(TRADES_FILE):
        return None

    try:
        import csv
        with open(TRADES_FILE, newline="") as f:
            rows = list(csv.DictReader(f))
            if not rows:
                return None

            last = rows[-1]

            if last.get("ticket") != last_ticket:
                return None
            if last.get("status") != "CLOSED":
                return None

            return {
                "ticket": last.get("ticket"),
                "result": last.get("result", "UNKNOWN"),
            }

    except Exception as e:
        print("⚠️ Error reading trades.csv:", e)
        return None


# =========================
# EXPLICIT EXPORTS
# =========================
__all__ = [
    "wait_for_market",
    "read_market",
    "send_command",
    "read_trade_exit",
]
