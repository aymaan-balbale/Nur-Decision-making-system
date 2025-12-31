import os
import time

# MT5 common files path
MT5_COMMON = os.path.expanduser(
    r"~\AppData\Roaming\MetaQuotes\Terminal\Common\Files"
)

MARKET_FILE = os.path.join(MT5_COMMON, "market.csv")
COMMAND_FILE = os.path.join(MT5_COMMON, "command.txt")


def wait_for_market():
    """Wait until MT5 starts writing market data"""
    print("⏳ Waiting for MT5 market.csv ...")
    while not os.path.exists(MARKET_FILE):
        time.sleep(1)
    print("✅ MT5 market feed detected")


def read_market():
    """Read latest market tick from MT5 CSV"""
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


def send_command(signal, sl, tp):
    """Send trade command to MT5"""
    with open(COMMAND_FILE, "w") as f:
        f.write(f"{signal},{sl},{tp}")

    print(f"📤 COMMAND SENT → {signal} | SL={sl} TP={tp}")
