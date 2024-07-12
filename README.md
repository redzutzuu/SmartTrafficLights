# Sistem Inteligent de Semaforizare

## Descrierea proiectului
Proiectul constă în realizarea unui sistem inteligent de semaforizare care detectează automat prezența vehiculelor sau pietonilor și ajustează semnalele semaforului în funcție de trafic. Acest sistem este controlat de un Raspberry Pi Zero 2W și diverse componente electronice, și include funcționalități pentru operare automată și manuală.
![Imagine proiect](<imagini proiect/proiect.jpg>)
### Interfață Web
![Interfata Web](<imagini proiect/interfataWeb.jpg>)
### Resurse:
- Raspberry Pi Zero 2W - 1x  
- Breadboard MB-102 - 1x
- Leduri:
  - 1x Led Roșu + Rezistență 220 ohm legat la GPIO25
  - 1x Led Galben + Rezistență 220 ohm legat la GPIO8
  - 1x Led Verde + Rezistență 220 ohm legat la GPIO7
- Buton (GPIO21) – 1x
- Senzor distanță HC-SR04 legat la 5V + GPIO4 + 1x Rezistență 330 ohm + 1x Rezistență 110 ohm – 1x
- Buzzer pasiv (GPIO15) – 1x
- Fire de conexiune – 20x
- Senzor de Temperatură și Umiditate DHT11 (GPIO18) + 1x rezistenta 10 kOhm

### Procesul de analiză și decizie:
Proiectul a fost motivat de necesitatea îmbunătățirii gestionării traficului în zonele urbane aglomerate, unde semafoarele tradiționale nu se adaptează dinamic la fluxul de trafic. Un sistem inteligent de semaforizare poate reduce congestia și poate îmbunătăți siguranța rutieră.

### Explorare Documentară:
Am identificat mai multe sisteme de gestionare a traficului care utilizează tehnologii similare:
1. **Intelligent Traffic Signal System:** Utilizarea de camere și senzori pentru a detecta vehicule și pietoni, ajustând semnalele semaforului în timp real.
2. **Adaptive Traffic Control System (ATCS):** Un sistem care ajustează timpii de semaforizare bazat pe fluxul de trafic detectat prin senzori și algoritmi de predicție.
3. **Smart Traffic Lights with IoT:** Utilizarea IoT pentru monitorizarea și controlul semafoarelor de la distanță, integrat cu rețele de trafic inteligente.

### Analiza resurselor:
Am ales Raspberry Pi Zero 2W datorită dimensiunilor reduse, costului accesibil și capacităților de calcul adecvate pentru gestionarea senzorilor și a interfețelor de control. Senzorul de distanță HC-SR04 a fost selectat pentru detectarea prezenței vehiculelor, iar LED-urile și butonul de control pentru semnalizarea și interacțiunea cu sistemul.

### Prezentare, realizare și implementare:
Sistemul inteligent de semaforizare include următoarele componente și funcționalități:
1. **Senzor de distanță HC-SR04:** Detectează prezența vehiculelor.
2. **LED-uri și rezistențe:** Indică starea semaforului (roșu, galben, verde).
3. **Buton de control:** Permite comutarea între modul automat și modul manual.
4. **Buzzer pasiv:** Emite un semnal sonor pentru atenționare.
5. **Senzorul de temperatură și umiditate:** Are rolul de a citi și afișa valorile curente ale temperaturii și umidității.

### Funcționare:
- **Mod automat:** Sistemul detectează vehiculele și ajustează semnalele semaforului pe baza distanței măsurate de senzorul HC-SR04.
- **Mod manual:** Utilizatorul poate schimba starea semaforului apăsând butonul de control.

### Schematica:
#### Schema electronica breadboard
![Schema electronica breadboard](<imagini proiect/Schema electronica breadboard.png>)

#### Schema electronica PCB
![Schema electronica pcb](<imagini proiect/Schema electronica pcb.png>)

#### Schema electronica
![Schema electronica](<imagini proiect/Schema electronica.png>)

## Codul proiectului:
Codul proiectului este scris în Python și utilizează biblioteci precum RPi.GPIO și gpiozero. Scriptul gestionează atât funcționarea automată, cât și cea manuală a semaforului, și include logica pentru detectarea prezenței vehiculelor și comutarea semnalelor semaforului. Codul complet poate fi găsit în repo-ul proiectului de pe [GitHub](https://github.tuiasi.ro/SM24/Semafor-1308A/).

```python
from flask import Flask, render_template, request, redirect, url_for
from gpiozero import Button, TrafficLights, DistanceSensor
from gpiozero.pins.pigpio import PiGPIOFactory
import Adafruit_DHT
import RPi.GPIO as GPIO
import time
from threading import Thread

app = Flask(__name__)
```
- **Flask**: Este framework-ul web pentru Python care permite dezvoltatorilor să creeze aplicații web.
- **gpiozero**: Este o bibliotecă Python care abstractizează și simplifică interacțiunea cu GPIO (General Purpose Input Output) pe Raspberry Pi.
- **Adafruit_DHT**: Este o bibliotecă Python pentru senzori de umiditate și temperatură de la Adafruit.
- **RPi.GPIO**: Bibliotecă pentru controlul pinurilor GPIO pe Raspberry Pi.
- **time**: Utilizată pentru a introduce întârzieri în program.
- **Thread**: Este o clasă din modulul standard threading care permite crearea și gestionarea firelor de execuție separate în Python.

```python
factory = PiGPIOFactory()
```
- Creează o instanță a clasei PiGPIOFactory pentru a utiliza pigpio ca backend pentru controlul pinurilor GPIO.

```python
button = Button(21, hold_time=3)
lights = TrafficLights(25, 8, 7)
ultrasonic = DistanceSensor(echo=17, trigger=4, pin_factory=factory)
```
- **button**: Inițializează un buton conectat la pinul 21.  hold_time=3 înseamnă că butonul trebuie ținut apăsat timp de 3 secunde pentru a declanșa un eveniment.
- **lights**: Inițializează un semafor cu LED-uri conectate la pinii 25 (verde), 8 (galben), și 7 (roșu).
- **ultrasonic**: Inițializează un senzor ultrasonic cu pini echo pe 17 și trigger pe 4.
```python
buzz_pin = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(buzz_pin, GPIO.OUT)
pwm = GPIO.PWM(buzz_pin, 1000)  # Inițializați un semnal PWM cu frecvența de 1 KHz
pwm.start(0)
```
-	**buzz_pin**: Pinul 26 este configurat ca ieșire pentru soneria pasivă.
-	**pwm**: Creează un obiect PWM pe pinul 15 cu o frecvență de 1000 Hz
```python
GREEN = 0
GREEN_YELLOW = 1
RED_YELLOW = 2
RED = 3
```
-	Stările semaforului sunt definite prin constante numerice pentru o gestionare mai ușoară.
```python
current_state = GREEN
automatic_mode = True
temperature = None
humidity = None
distance = None
```
-	**current_state**: Starea curentă a semaforului, inițializată la verde.
-	**automatic_mode**: Modul de operare, inițializat la automat (True).
-	**temperature**: Temperatura, inițializată cu valoarea None.
-	**humidity**: Umiditatea, inițializată cu valoarea None.
-	**distance**: Distanta, inițializată cu valoarea None.
```python
def update_lights(state):
    print(f"Updating lights to state: {state}")
    if state == GREEN:
        lights.green.on()
        lights.amber.off()
        lights.red.off()
        pwm.stop()
    elif state == GREEN_YELLOW:
        lights.green.on()
        lights.amber.on()
        lights.red.off()
        pwm.stop()
    elif state == RED_YELLOW:
        lights.green.off()
        lights.amber.on()
        lights.red.on()
        pwm.stop()
    elif state == RED:
        lights.green.off()
        lights.amber.off()
        lights.red.on()
        pwm.start(50)  # Porniți PWM cu un ciclu de lucru de 50% pentru a suna soneria
```
-	Această funcție actualizează starea LED-urilor și controlează soneria pasivă în funcție de starea curentă.
```python
def button_held():
    global automatic_mode
    automatic_mode = not automatic_mode
    if automatic_mode:
        print("Switched to automatic mode")
    else:
        print("Switched to manual mode")
```
-	Această funcție comută între modul automat și manual atunci când butonul este ținut apăsat timp de 3 secunde.
```python
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
```
-	Această funcție schimbă manual stările semaforului atunci când butonul este apăsat.
```python
button.when_pressed = button_pressed
button.when_held = button_held
```
-	Atribuie funcțiile button_pressed și button_held evenimentelor respective ale butonului.
```python
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

sensor = Adafruit_DHT.DHT11
pin = 18
```
-	Măsurarea Distanței: folosind un senzor ultrasonor și o convertește în centimetri (cm). Valoarea măsurată este stocată în variabila distance.
-	Actualizarea Stării: Semaforul este actualizat în funcție de distanța măsurată.
-	Întârziere: O pauză de 0.5 secunde pentru a preveni apăsările duble accidentale
```python
def read_dht11():
    global temperature, humidity
    humidity, temperature = Adafruit_DHT.read(sensor, pin)
    if humidity is not None and temperature is not None:
        print(f'Temperature: {temperature:.1f}°C')
        print(f'Humidity: {humidity:.1f}%')
    else:
        print('Failed to get reading. Try again!')
```
-	Are rolul de a citi datele de la un senzor DHT11 (sau DHT22) pentru temperatura și umiditate și de a le stoca în variabilele globale temperature și humidity.
```python
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
```
- **Route pentru pagina principală ('/')**:
  - Afișează starea curentă a semaforului, temperatura și umiditatea măsurate.
  - Dacă aplicația este în mod automat, afișează "Automatic"; altfel, afișează "Manual".
  - Utilizează un șablon HTML (index.html) pentru a afișa informațiile.

- **Route pentru schimbarea modului ('/switch_mode')**:
  - Schimbă între modul automat și manual al aplicației.
  - Este activat prin trimiterea unei cereri POST.

- **Route pentru setarea stării semaforului ('/set_state')**:
  - Permite utilizatorului să seteze manual starea semaforului.
  - Este activat prin trimiterea unei cereri POST cu starea dorită.

## Rezultatul final:
Proiectul demonstrează un sistem de semaforizare inteligent, capabil să gestioneze traficul eficient, adaptându-se automat la prezența vehiculelor. Sistemul permite și controlul manual, oferind flexibilitate și fiabilitate în diverse scenarii urbane. Utilizarea componentelor accesibile și a unei abordări modulare face ca acest proiect să fie scalabil și ușor de implementat în diverse contexte urbane.

## Link-uri Utilitare
- Repo-ul cu codul proiectului: [GitHub Repo](https://github.tuiasi.ro/SM24/Semafor-1308A)
- Documentația proiectului pe GitHub: [GitHub README](https://github.tuiasi.ro/SM24/Semafor-1308A#readme)
- Documentația proiectului pe hackster.io: [Documentatie hackster.io](https://www.hackster.io/larisa-andreeapetrisor/semafor-492faa)

### Inspirație:
- [Sursa 1](https://projects.raspberrypi.org/en/projects/physical-computing/9)
- [Sursa 2](https://projects.raspberrypi.org/en/projects/physical-computing/12)

## Concluzie
Proiectul Semafor Inteligent demonstrează cum tehnologia poate fi utilizată pentru a îmbunătăți eficiența traficului urban. Utilizarea componentelor accesibile și a unei abordări modulare face ca acest proiect să fie scalabil și ușor de implementat în diverse contexte urbane.
