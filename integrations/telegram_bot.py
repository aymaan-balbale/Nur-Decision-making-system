import csv
from pathlib import Path
import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

TRADES_FILE = Path("logs/trades_log.csv")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN not set")

# ---------- Commands ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Nur Trading Bot online.\n\n"
        "Commands:\n"
        "/status\n"
        "/last_trade\n"
        "/help"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/status – system status\n"
        "/last_trade – last completed trade\n"
        "/help – this message"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # placeholder – we wire real data later
    await update.message.reply_text(
        "STATUS\n"
        "Market: XAUUSD\n"
        "State: WAITING\n"
        "EMA200: warming up"
    )

async def last_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not TRADES_FILE.exists():
        await update.message.reply_text("No completed trades yet.")
        return

    import csv

    with TRADES_FILE.open(newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        await update.message.reply_text("No completed trades yet.")
        return

    t = rows[-1]  # last completed trade

    msg = (
        "LAST TRADE\n"
        f"ID: {t['trade_id']}\n"
        f"Side: {t['direction']}\n"
        f"Entry: {t['entry_price']}\n"
        f"Exit: {t['exit_price']}\n"
        f"PnL: {t['pnl']} ({t['pnl_pct']})\n"
        f"Reason: {t['exit_reason']}\n"
        f"Entry Time: {t['entry_time']}\n"
        f"Exit Time: {t['exit_time']}\n"
        f"Candles: {t['candles_in_trade']}"
    )

    await update.message.reply_text(msg)


# ---------- Runner ----------

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("last_trade", last_trade))

    print("Telegram bot running...")
    await app.run_polling()

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("last_trade", last_trade))

    print("Telegram bot running...")
    app.run_polling()
