📌 Project Title

MT5 EMA200 Trading Prototype (Python ↔ MQL5 Bridge)

🧠 Project Description

This repository contains a working prototype of an algorithmic trading system for MetaTrader 5 (MT5) built using a Python ↔ MQL5 bridge architecture.

The system demonstrates how Python-based strategy logic can interact with MT5 Expert Advisors in real time without using any unofficial or unsafe APIs.

The prototype focuses on a single, clear strategy:

EMA 200 crossover on M1 timeframe (XAUUSD)

⚙️ How the Prototype Works
🔄 Architecture Overview
MT5 Expert Advisor (MQL5)
        ↓
 Writes live market data to CSV
        ↓
Python Engine reads CSV in real time
        ↓
Python calculates EMA200 & trade logic
        ↓
Python outputs trade command
        ↓
MT5 EA executes trade


This approach acts as a custom MT5 trading API, fully compliant with MetaTrader rules.

📈 Strategy Logic (Prototype Scope)

Timeframe: M1

Indicator: EMA 200

Logic:

Detect candle close above/below EMA200

Confirm BUY / SELL setup

Auto-calculate:

Entry

Stop Loss (SL)

Take Profit (TP)

Outputs clear trade commands

🧪 What This Prototype Proves

✅ Live market data flow from MT5
✅ Real-time Python strategy execution
✅ Stable MT5 ↔ Python communication
✅ Correct EMA200 calculations
✅ Confirmed trade signal generation
✅ Production-ready architecture foundation

🚧 Prototype Limitations (Intentional)

This is a prototype, not a full trading bot.

Not included:

Money management

Position sizing

Multi-symbol handling

Risk % control

Order execution optimization

Error recovery logic

These are planned for future iterations.

🛠️ Tech Stack

MetaTrader 5

MQL5 (Expert Advisor)

Python 3

CSV-based IPC (Inter-Process Communication)

🎯 Use Case

This project is ideal for:

Learning algorithmic trading with MT5

Understanding Python ↔ MT5 integration

Building a foundation for advanced trading systems

Demonstrating a working trading prototype

🟢 Current Status

✔ Prototype complete
✔ Strategy validated
✔ Live data confirmed
✔ Ready for enhancement
