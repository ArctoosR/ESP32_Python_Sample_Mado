import network
import socket
import time
from machine import Pin, PWM

# تنظیمات Wi-Fi
SSID = "REPLACE_WITH_YOUR_SSID"
PASSWORD = "REPLACE_WITH_YOUR_PASSWORD"

# راه‌اندازی PWM روی GPIO 2
pwm_pin = PWM(Pin(2))
pwm_pin.freq(1000)  # تنظیم فرکانس PWM
pwm_pin.duty(512)   # مقدار پیش‌فرض (بین ۰ تا ۱۰۲۳)

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
            pass

    # **صفحه HTML با ولوم دایره‌ای**
    response = """HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { text-align: center; font-family: Arial, sans-serif; }
.knob-container { display: flex; justify-content: center; align-items: center; height: 300px; }
.knob { width: 150px; height: 150px; border-radius: 50%; background: radial-gradient(circle, #ddd, #888); box-shadow: inset 5px 5px 15px rgba(0,0,0,0.2), inset -5px -5px 15px rgba(255,255,255,0.3); position: relative; }
.knob:after { content: ''; width: 10px; height: 30px; background: #333; position: absolute; top: 10px; left: calc(50% - 5px); border-radius: 5px; }
</style>
</head>
<body>
<h1>ESP32 PWM Control</h1>
<div class="knob-container">
    <div id="knob" class="knob"></div>
</div>
<p>PWM Value: <span id="pwmValue">512</span></p>
<script>
let knob = document.getElementById('knob');
let pwmDisplay = document.getElementById('pwmValue');
let startAngle = 0; 
let currentAngle = 0;

knob.addEventListener('mousedown', startRotation);
knob.addEventListener('touchstart', startRotation, { passive: true });

function startRotation(event) {
    let pos = event.touches ? event.touches[0] : event;
    let rect = knob.getBoundingClientRect();
    let centerX = rect.left + rect.width / 2;
    let centerY = rect.top + rect.height / 2;

    let dx = pos.clientX - centerX;
    let dy = pos.clientY - centerY;

    startAngle = Math.atan2(dy, dx) * (180 / Math.PI);  

    document.addEventListener('mousemove', rotateKnob);
    document.addEventListener('touchmove', rotateKnob, { passive: true });

    document.addEventListener('mouseup', stopRotation);
    document.addEventListener('touchend', stopRotation);
}

function rotateKnob(event) {
    let pos = event.touches ? event.touches[0] : event;
    let rect = knob.getBoundingClientRect();
    let centerX = rect.left + rect.width / 2;
    let centerY = rect.top + rect.height / 2;

    let dx = pos.clientX - centerX;
    let dy = pos.clientY - centerY;

    let newAngle = Math.atan2(dy, dx) * (180 / Math.PI);
    let deltaAngle = newAngle - startAngle;
    startAngle = newAngle;  

    currentAngle += deltaAngle;
    currentAngle = Math.max(0, Math.min(360, currentAngle));  

    let pwmValue = Math.round((currentAngle / 360) * 1023);

    knob.style.transform = `rotate(${currentAngle}deg)`;
    pwmDisplay.innerText = pwmValue;

    fetch("/pwm?value=" + pwmValue);
}

function stopRotation() {
    document.removeEventListener('mousemove', rotateKnob);
    document.removeEventListener('touchmove', rotateKnob);
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
