📌 Nur Trading Agent
MT5 EMA200 Algorithmic Trading Prototype (Python ↔ MQL5)
🧠 Project Overview

Nur Trading Agent is a working prototype of an algorithmic trading system designed to demonstrate how Python-based trading logic can be safely and cleanly integrated with MetaTrader 5 (MT5) using an official Expert Advisor (EA) execution layer.

The project follows a separation-of-concerns architecture, where:

Python handles decision-making and strategy logic

MT5 (MQL5 EA) handles market data access and trade execution

This ensures stability, safety, and compliance with MT5’s design principles.

🎯 Core Objective

Implement a real-time EMA200 crossover strategy

Execute trades on MT5 using official EA execution

Avoid unofficial or unsafe APIs

Demonstrate live market integration (demo / test environment)

Provide a strong foundation for future enhancements

🏗️ System Architecture
MT5 Terminal (MQL5 EA)
        ↓
   market.csv (live data)
        ↓
Python Trading Engine
        ↓
   command.txt (trade orders)
        ↓
MT5 EA executes trades

Design Principles

Execution layer never contains strategy logic

Strategy layer never touches broker directly

Clean IPC via file-based bridge

Failure isolation (Python crash ≠ MT5 crash)

📈 Trading Strategy

Indicator:

EMA 200

Timeframe:

M1 (1-minute)

Logic:

BUY when price crosses above EMA200

SELL when price crosses below EMA200

One signal per crossover (no trade spamming)

Risk Controls (Prototype Level):

Fixed SL / TP (demo values)

Duplicate trade prevention

⚙️ Technology Stack

MetaTrader 5

MQL5 (Expert Advisor)

Python 3

CSV-based IPC (Inter-Process Communication)

No third-party or unofficial MT5 APIs are used.

🚀 Features Implemented

✅ Live market data feed from MT5

✅ Real-time EMA200 calculation in Python

✅ BUY / SELL signal generation

✅ Trade execution via MT5 EA

✅ Demo-safe trading workflow

✅ GitHub security-compliant (no secrets in repo)

🚧 Intentional Limitations

This repository is a prototype, not a production trading bot.

Not included (by design):

Position sizing

Advanced money management

Multi-symbol support

News filtering

High-frequency execution

These can be added in future iterations.

🧪 Usage (Demo / Test Environment)

Open MetaTrader 5

Attach the provided EA to XAUUSD (M1)

Enable Algo Trading

Run Python engine:

python main.py


The system will:

Listen to live market data

Detect EMA200 crossovers

Send trade commands to MT5

🔐 Security Note

No API keys or secrets are stored in this repository

All sensitive credentials were intentionally removed

The project complies with GitHub Push Protection rules

🎓 Academic / Learning Use

This project is suitable for:

Algorithmic trading demonstrations

MT5 integration learning

System architecture case studies

College / academic submissions

🟢 Project Status

✔ Live MT5 integration complete

✔ Strategy validated in real-time

✔ Trade execution confirmed (test environment)

✔ Repository cleaned and secured

📌 One-Line Summary

A real-time EMA200 trading prototype using Python for strategy logic and MetaTrader 5 Expert Advisor for official trade execution.
