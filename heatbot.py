#!/usr/bin/env python3
import adafruit_dht
import board
import time
import schedule
import threading

from telegram import Bot, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
# === CONFIG ===
BOT_TOKEN = '7636381534:AAGLVrRfKwcMNiOqud_XqJgyDnfkeI81dbk'
CHAT_ID = '583154813'  # your personal chat ID
SEND_INTERVAL_MINUTES = 10  # configurable interval in minutes

# === SETUP DHT ===
dht = adafruit_dht.DHT11(board.D26)

# === SAFE READ FUNCTION ===
def safe_read():
    """
    Attempt to read temp and humidity until valid values are obtained.
    Retries indefinitely with 1s delay on failure or None values.
    """
    while True:
        try:
            t = dht.temperature
            h = dht.humidity
            if t is not None and h is not None:
                return t, h
        except Exception:
            # ignore and retry
            pass
        time.sleep(1)

# === READ HELPERS ===
def read_temperature() -> str:
    t, _ = safe_read()
    return f"{t:.1f}°C"

def read_humidity() -> str:
    _, h = safe_read()
    return f"{h:.1f}%"

def read_both() -> str:
    t, h = safe_read()
    return f"🌡️ Temp: {t:.1f}°C\n💧 Humidity: {h:.1f}%"

# === SETUP TELEGRAM ===
bot = Bot(token=BOT_TOKEN)
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# — /status command —
def status(update: Update, context: CallbackContext):
    update.message.reply_text(read_both())

dispatcher.add_handler(CommandHandler("status", status))

# — text handler for “temp”, “humidity”, “all” —
def handle_text(update: Update, context: CallbackContext):
    txt = update.message.text.strip().lower()
    if txt == "temp":
        update.message.reply_text(f"🌡️ Temperature is {read_temperature()}")
    elif txt == "humidity":
        update.message.reply_text(f"💧 Humidity is {read_humidity()}")
    elif txt == "all":
        update.message.reply_text(read_both())

# register text handler
message_filter = Filters.text & ~Filters.command
dispatcher.add_handler(MessageHandler(message_filter, handle_text))

# — periodic send —
def send_reading():
    bot.send_message(chat_id=CHAT_ID, text=read_both())

schedule.every(SEND_INTERVAL_MINUTES).minutes.do(send_reading)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

thread = threading.Thread(target=run_schedule, daemon=True)
thread.start()

# — start bot —
print(f"🚀 HeatBot started. Interval: {SEND_INTERVAL_MINUTES} min.\n"
      "Use /status or text 'temp', 'humidity', 'all'.")
updater.start_polling()
updater.idle()
