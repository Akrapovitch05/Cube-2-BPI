import time
import json
import socket
import subprocess
import paho.mqtt.client as mqtt
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# MQTT settings
mqtt_server = "192.168.32.58"
mqtt_topic_temperature = "sensor/temperature"
mqtt_topic_humidity = "sensor/humidity"

# Initialize the SSD1306 OLED display
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

# Initialize temperature and humidity variables
temperature = 0
humidity = 0

# Function to get IP address
def get_ip_address():
    ip_address = ""
    try:
        ip_address = subprocess.check_output(['hostname', '-I']).decode().strip()
    except:
        ip_address = "Error: Unable to get IP address"
    return ip_address

# Callback function when MQTT client receives a message
def on_message(client, userdata, message):
    global temperature, humidity

    if message.topic == mqtt_topic_temperature:
        temperature = float(message.payload.decode())
    elif message.topic == mqtt_topic_humidity:
        humidity = float(message.payload.decode())

    # Update the OLED display with temperature, humidity, time, and IP address
    with canvas(device) as draw:
        draw.text((10, 0), f"IP: {get_ip_address()}", fill="white")
        draw.text((10, 15), f"Time: {time.strftime('%H:%M:%S', time.localtime(time.time() + 3600))}", fill="white")
        draw.text((10, 30), f"Temp: {temperature} C", fill="white")
        draw.text((10, 45), f"Humidity: {humidity} %", fill="white")

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(mqtt_topic_temperature)
    client.subscribe(mqtt_topic_humidity)

def main():
    # Initialize MQTT client
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(mqtt_server, 1883, 60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()

if __name__ == "__main__":
    main()
