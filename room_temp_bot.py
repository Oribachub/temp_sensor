#!/usr/bin/env python3
import adafruit_dht
import board
import time
import schedule
import threading
import csv
import os
from datetime import datetime

from telegram import Bot, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

# === CONFIGURATION ===
BOT_TOKEN = '7636381534:AAGLVrRfKwcMNiOqud_XqJgyDnfkeI81dbk'
CHAT_ID = '583154813'  # your personal chat ID
SEND_INTERVAL_MINUTES = 1        # Interval for automated sends (in minutes)
LOG_FILE = 'sensor_log.csv'      # CSV log file path

# === SETUP SENSOR ===
dht = adafruit_dht.DHT11(board.D26)

# === SAFE READ FUNCTION ===
def safe_read():
    """
    Continuously attempt to read from the DHT11 until valid values are returned.
    """
    while True:
        try:
            temperature = dht.temperature
            humidity = dht.humidity
            if temperature is not None and humidity is not None:
                return temperature, humidity
        except Exception:
            pass
        time.sleep(1)

# === CSV LOGGING ===
def log_reading(temperature, humidity, status='OK', error_msg=''):
    """
    Append a reading to the CSV log. Creates header if file does not exist.
    """
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["timestamp","temperature_C","humidity_pct","status","error"])
        timestamp = datetime.now().isoformat()
        writer.writerow([
            timestamp,
            f"{temperature:.1f}",
            f"{humidity:.1f}",
            status,
            error_msg
        ])

# === TELEGRAM BOT SETUP ===
bot = Bot(token=BOT_TOKEN)
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# === COMMAND HANDLERS ===
def status(update: Update, context: CallbackContext):
    """Reply with both temp and humidity"""
    temperature, humidity = safe_read()
    text = f"🌡️ Temp: {temperature:.1f}°C\n💧 Humidity: {humidity:.1f}%"
    update.message.reply_text(text)

# Register /status
dispatcher.add_handler(CommandHandler("status", status))

# === MESSAGE HANDLER ===
def handle_text(update: Update, context: CallbackContext):
    txt = update.message.text.strip().lower()
    if txt == 'temp':
        temperature, _ = safe_read()
        update.message.reply_text(f"🌡️ Temperature: {temperature:.1f}°C")
    elif txt == 'humidity':
        _, humidity = safe_read()
        update.message.reply_text(f"💧 Humidity: {humidity:.1f}%")
    elif txt == 'all':
        temperature, humidity = safe_read()
        update.message.reply_text(f"🌡️ Temp: {temperature:.1f}°C\n💧 Humidity: {humidity:.1f}%")

# Register text handler (ignore commands)
dispatcher.add_handler(
    MessageHandler(Filters.text & ~Filters.command, handle_text)
)

# === PERIODIC SENDER ===
def send_reading():
    """Read sensor, log it, and send via Telegram"""
    try:
        temperature, humidity = safe_read()
        log_reading(temperature, humidity)
        bot.send_message(
            chat_id=CHAT_ID,
            text=f"🌡️ Temp: {temperature:.1f}°C\n💧 Humidity: {humidity:.1f}%"
        )
    except Exception as e:
        # Log the error but do not send
        log_reading(0, 0, status='ERROR', error_msg=str(e))

# Schedule the periodic task
schedule.every(SEND_INTERVAL_MINUTES).minutes.do(send_reading)

# Background thread to run schedule

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

thread = threading.Thread(target=run_schedule, daemon=True)
thread.start()

# === START BOT ===
print(
    f"🚀 HeatBot started: sends every {SEND_INTERVAL_MINUTES} min, logs to {LOG_FILE}\n"
    "Use /status or text 'temp', 'humidity', 'all'."
)
updater.start_polling()
updater.idle()

