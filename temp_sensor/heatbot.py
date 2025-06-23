from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import adafruit_dht
import board
import time
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import schedule
import threading
# === CONFIG ===
BOT_TOKEN = '7636381534:AAGLVrRfKwcMNiOqud_XqJgyDnfkeI81dbk'
CHAT_ID = '7636381534'  # your personal chat ID


# === Setup DHT ===
dhtDevice = adafruit_dht.DHT11(board.D26)

# === Setup Telegram Bot ===
bot = Bot(token=BOT_TOKEN)
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# === Function to read sensor ===
def read_dht():
    try:
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        if temperature_c is not None and humidity is not None:
            return f"?? Temp: {temperature_c}°C\n? Humidity: {humidity}%"
        else:
            return "Failed to read DHT."
    except Exception as e:
        return f"Error: {e}"

# === Send reading to user ===
def send_reading():
    message = read_dht()
    bot.send_message(chat_id=CHAT_ID, text=message)

# === Handler for /status command ===
def status(update: Update, context: CallbackContext):
    message = read_dht()
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

status_handler = CommandHandler('status', status)
dispatcher.add_handler(status_handler)

# === Schedule hourly sending ===
schedule.every().hour.do(send_reading)

# === Thread to run schedule in background ===
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule_thread = threading.Thread(target=run_schedule)
schedule_thread.daemon = True
schedule_thread.start()

# === Start bot polling ===
print("Bot is running. Type /status in your Telegram to get a reading.")
updater.start_polling()
updater.idle()
