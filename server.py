#!flask/bin/python
from flask import Flask
from brightpilib import *
import picamera
from time import sleep

app = Flask(__name__)
brightPi = BrightPi()
brightPi.reset()
camera = picamera.PiCamera()

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/photo/<option>')
def takePicture(option):
    if(option == 'dark'):
        brightPi.reset()
        brightPi.set_led_on_off(LED_IR, ON)
    camera.capture('image1.jpg')
    sleep(5)
    brightPi.set_led_on_off(LED_IR, OFF)


if (__name__ == '__main__'):
    app.run(debug=True)