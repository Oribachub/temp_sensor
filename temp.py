import adafruit_dht
import board
import time

# Initialize the DHT11 using GPIO26 (BCM 26)
dhtDevice = adafruit_dht.DHT11(board.D26)

try:
    while True:
        try:
            # Read temperature and humidity
            temperature_c = dhtDevice.temperature
            humidity = dhtDevice.humidity

            if temperature_c is not None and humidity is not None:
                print(f"Temp: {temperature_c}°C  Humidity: {humidity}%")
            else:
                print("Failed to get reading. Trying again...")

        except RuntimeError as error:
            # Reading doesn't always succeed on first try
            print(f"Runtime error: {error}")

        time.sleep(2)

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    dhtDevice.exit()

