#!flask/bin/python
from flask import Flask, jsonify, render_template, Response 
from brightpilib import *
import picamera
from time import sleep
import cv2
import socket 
import io 

app = Flask(__name__)
brightPi = BrightPi()
brightPi.reset()
camera = picamera.PiCamera()
vc = cv2.VideoCapture(0) 


@app.route('/')
def index():
    """Video streaming .""" 
   return render_template('index.html') 

@app.route('/photo/<option>')
def takePicture(option):
    if(option == 'dark'):
        brightPi.reset()
        brightPi.set_led_on_off(LED_IR, ON)
    camera.capture('image1.jpg')
    sleep(5)
    brightPi.set_led_on_off(LED_IR, OFF)
    resp = jsonify(success=True)
    resp.status_code = 200
    return resp

def gen(): 
   """Video streaming generator function.""" 
   while True: 
       rval, frame = vc.read() 
       cv2.imwrite('pic.jpg', frame) 
       yield (b'--frame\r\n' 
              b'Content-Type: image/jpeg\r\n\r\n' + open('pic.jpg', 'rb').read() + b'\r\n') 

@app.route('/video_feed') 
def video_feed(): 
   """Video streaming route. Put this in the src attribute of an img tag.""" 
   return Response(gen(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame') 

if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=80)


#sudo  LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0  python3 server.py

