import time
import os

FILE_PATH = r"C:\Users\Abusahil\AppData\Roaming\MetaQuotes\Terminal\Common\Files\market.csv"

print("=== MT5 MARKET READER (LIVE) ===")
print("Reading:", FILE_PATH)
print("Press CTRL+C to stop\n")

last_seen = ""

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
