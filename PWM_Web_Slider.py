import network
import socket
import time
from machine import Pin, PWM

# تنظیمات شبکه WiFi
SSID = "REPLACE_WITH_YOUR_SSID"
PASSWORD = "REPLACE_WITH_YOUR_PASSWORD"

# راه‌اندازی PWM روی GPIO 2
pwm_pin = PWM(Pin(2))
pwm_pin.freq(1000)  # تنظیم فرکانس PWM
pwm_pin.duty(512)   # مقدار پیش‌فرض (۰ تا ۱۰۲۳)

# اتصال به Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    time.sleep(0.5)
    print("Connecting...")

print("WiFi connected.")
print("IP address:", wlan.ifconfig()[0])

# راه‌اندازی سرور وب
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 80))
server.listen(5)

def handle_request(client):
    request = client.recv(1024).decode("utf-8")
    print(request)

    # دریافت مقدار PWM از درخواست‌های HTTP
    if "GET /pwm?value=" in request:
        try:
            pwm_value = int(request.split("value=")[-1].split()[0])
            if 0 <= pwm_value <= 1023:  # بررسی محدوده صحیح PWM
                pwm_pin.duty(pwm_value)
                print(f"PWM set to: {pwm_value}")
        except ValueError:
            pass  # اگر مقدار نامعتبر باشد، نادیده گرفته شود

    # صفحه HTML با اسلایدر برای کنترل PWM
    response = """HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
html { font-family: Helvetica; text-align: center; }
.slider { width: 80%; margin: 20px auto; }
</style>
</head>
<body>
<h1>ESP32 PWM Control</h1>
<p>PWM Value: <span id="pwmValue">512</span></p>
<input type="range" id="pwmSlider" min="0" max="1023" value="512" class="slider"
    oninput="updatePWM(this.value)">
<script>
function updatePWM(value) {
    document.getElementById('pwmValue').innerText = value;
    fetch("/pwm?value=" + value);
}
</script>
</body>
</html>
"""
    
    client.send(response)
    client.close()

# حلقه اصلی سرور برای دریافت درخواست‌ها
while True:
    client, addr = server.accept()
    handle_request(client)
