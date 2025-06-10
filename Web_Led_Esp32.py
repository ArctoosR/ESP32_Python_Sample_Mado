import network
import socket
import time
from machine import Pin

# Replace with your network credentials
SSID = "REPLACE_WITH_YOUR_SSID"
PASSWORD = "REPLACE_WITH_YOUR_PASSWORD"

# Set up GPIO pins
output12 = Pin(2, Pin.OUT)
output14 = Pin(14, Pin.OUT)
output12.value(0)
output14.value(0)

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    time.sleep(0.5)
    print("Connecting...")

print("WiFi connected.")
print("IP address:", wlan.ifconfig()[0])

# Start web server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 80))
server.listen(5)

def handle_request(client):
    request = client.recv(1024).decode("utf-8")
    print(request)
    
    if "GET /12/on" in request:
        output12.value(1)
    elif "GET /12/off" in request:
        output12.value(0)
    elif "GET /14/on" in request:
        output14.value(1)
    elif "GET /14/off" in request:
        output14.value(0)

    response = """HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
html {{ font-family: Helvetica; text-align: center; }}
.button {{ background-color: #4CAF50; color: white; padding: 16px 40px; font-size: 30px; margin: 2px; cursor: pointer; }}
.button2 {{ background-color: #555555; }}
</style>
</head>
<body>
<h1>ESP32 Web Server</h1>
<p>GPIO 12 - State {}</p>
<p><a href="/12/{}/"><button class="button {}">{} </button></a></p>
<p>GPIO 14 - State {}</p>
<p><a href="/14/{}/"><button class="button {}">{} </button></a></p>
</body>
</html>
""".format(
    "on" if output12.value() else "off",
    "off" if output12.value() else "on",
    "button2" if output12.value() else "",
    "OFF" if output12.value() else "ON",
    "on" if output14.value() else "off",
    "off" if output14.value() else "on",
    "button2" if output14.value() else "",
    "OFF" if output14.value() else "ON"
)

    client.send(response)
    client.close()

while True:
    client, addr = server.accept()
    handle_request(client)
