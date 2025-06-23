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
CHAT_ID = '7636381534'  # your personal chat ID

# === SETUP DHT ===
dht = adafruit_dht.DHT11(board.D26)

def read_temperature() -> str:
    try:
        t = dht.temperature
        return f"{t:.1f}°C" if t is not None else "N/A"
    except Exception:
        return "Error reading temperature"

def read_humidity() -> str:
    try:
        h = dht.humidity
        return f"{h:.1f}%" if h is not None else "N/A"
    except Exception:
        return "Error reading humidity"

def read_both() -> str:
    t = read_temperature()
    h = read_humidity()
    return f"🌡️ Temp: {t}\n💧 Humidity: {h}"

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
    # else: you can ignore or send a help message
    # else:
    #     update.message.reply_text("Send 'temp', 'humidity' or 'all'.")

dispatcher.add_handler(
    MessageHandler(Filters.text & ~Filters.command, handle_text)
)

# — hourly push —
def send_reading():
    bot.send_message(chat_id=CHAT_ID, text=read_both())

schedule.every(15).seconds.do(send_reading)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

thread = threading.Thread(target=run_schedule, daemon=True)
thread.start()

# — start polling —
print("🚀 HeatBot started. Send /status, or just text 'temp', 'humidity' or 'all'.")
updater.start_polling()
updater.idle()
