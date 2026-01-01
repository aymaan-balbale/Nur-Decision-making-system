"""
MT5 Market Data Reader - Live monitoring of MT5 market.csv file.

This utility reads and displays real-time market data from MT5 terminal
for debugging and monitoring purposes.
"""

import time
import os

FILE_PATH = r"C:\Users\Abusahil\AppData\Roaming\MetaQuotes\Terminal\Common\Files\market.csv"

print("=== MT5 MARKET READER (LIVE) ===")
print("Reading:", FILE_PATH)
print("Press CTRL+C to stop\n")

last_seen: str = ""

while True:
    try:
        if os.path.exists(FILE_PATH):
            with open(FILE_PATH, "r", encoding="utf-16") as f:
                data = f.read().strip()

            if data and data != last_seen:
                print(data)
                last_seen = data

        time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nStopped by user")
        break

    except Exception as e:
        print("Error:", e)
        time.sleep(1)
