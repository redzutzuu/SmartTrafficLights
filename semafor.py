# importam cele necesare din Flask pentru a crea o aplicatie web
from flask import Flask, render_template, request, redirect, url_for
# gpiozero ne ajuta sa putem controla componentele GPIO pe Raspberry Pi
from gpiozero import Button, TrafficLights, DistanceSensor
from gpiozero.pins.pigpio import PiGPIOFactory
# biblioteca pentru citirea senzorilor de tempereratura si umiditate DHT
import Adafruit_DHT
import RPi.GPIO as GPIO
import time
from threading import Thread

app = Flask(__name__)

# Creează o instanță PiGPIOFactory
factory = PiGPIOFactory()

# Creează instanțe pentru semafor, buton și senzor ultrasonic
button = Button(21, hold_time=3)
lights = TrafficLights(25, 8, 7)
ultrasonic = DistanceSensor(echo=17, trigger=4, pin_factory=factory)

# Configurare pentru buzzer pasiv
buzz_pin = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzz_pin, GPIO.OUT)
pwm = GPIO.PWM(buzz_pin, 1000)
pwm.start(0)

# Definește stările pentru fiecare LED
GREEN = 0
GREEN_YELLOW = 1
RED_YELLOW = 2
RED = 3

# Inițializează variabile
current_state = GREEN
automatic_mode = True
temperature = None
humidity = None
distance = None

# Funcție pentru actualizarea semaforului
def update_lights(state):
    print(f"Updating lights to state: {state}")
    if state == GREEN:
        lights.green.on()
        lights.amber.off()
        lights.red.off()
        pwm.ChangeDutyCycle(0)
    elif state == GREEN_YELLOW:
        lights.green.on()
        lights.amber.on()
        lights.red.off()
        pwm.ChangeDutyCycle(0)
    elif state == RED_YELLOW:
        lights.green.off()
        lights.amber.on()
        lights.red.on()
        pwm.ChangeDutyCycle(0)
    elif state == RED:
        lights.green.off()
        lights.amber.off()
        lights.red.on()
        pwm.ChangeDutyCycle(50)

# Funcție apelată când butonul este ținut apăsat
# Aceasta functie face schimbarea intre modul automat si modul manual al semaforului
def button_held():
    global automatic_mode
    automatic_mode = not automatic_mode
    if automatic_mode:
        print("Switched to automatic mode")
    else:
        print("Switched to manual mode")

# Funcție apelată când butonul este apăsat
# Atunci cand sunt suntem in modul manual la apasarea butonului se schimba starea semaforului
def button_pressed():
    global current_state
    if not automatic_mode:
        if current_state == GREEN:
            current_state = GREEN_YELLOW
        elif current_state == GREEN_YELLOW:
            current_state = RED_YELLOW
        elif current_state == RED_YELLOW:
            current_state = RED
        elif current_state == RED:
            current_state = GREEN
        update_lights(current_state)
        print(f"Manual mode: Changed to state {current_state}")

# Asociază funcțiile butonului
button.when_pressed = button_pressed
button.when_held = button_held

# Funcție pentru controlul automat al semaforului
def automatic_control():
    global current_state, distance
    while True:
        if automatic_mode:
            distance = ultrasonic.distance * 100  # Convert distance to cm
            print(f"Distance measured: {distance} cm")
            if distance > 40:
                current_state = GREEN
            elif distance > 20:
                current_state = GREEN_YELLOW
            elif distance > 10:
                current_state = RED_YELLOW
            else:
                current_state = RED
            update_lights(current_state)
        time.sleep(0.5)

# Configurare pentru senzorul DHT11
sensor = Adafruit_DHT.DHT11
pin = 18

# Funcție pentru citirea datelor de la senzorul DHT11
def read_dht11():
    global temperature, humidity
    humidity, temperature = Adafruit_DHT.read(sensor, pin)
    if humidity is not None and temperature is not None:
        print(f'Temperature: {temperature:.1f}°C')
        print(f'Humidity: {humidity:.1f}%')
    else:
        print('Failed to get reading. Try again!')

@app.route('/')
def index():
    global current_state, automatic_mode, temperature, humidity, distance
    read_dht11()
    return render_template('index.html', mode="Automatic" if automatic_mode else "Manual", state=current_state, temperature=temperature, humidity=humidity, distance=distance)

@app.route('/switch_mode', methods=['POST'])
def switch_mode():
    global automatic_mode
    automatic_mode = not automatic_mode
    return redirect(url_for('index'))

@app.route('/set_state', methods=['POST'])
def set_state():
    if not automatic_mode:
        state = int(request.form.get('state'))
        update_lights(state)
    return redirect(url_for('index'))

if __name__ == '__main__':
    thread = Thread(target=automatic_control)
    thread.daemon = True
    thread.start()
    app.run(host='0.0.0.0', port=5000)
