#!flask/bin/python
from flask import Flask, jsonify, render_template, Response 
from brightpilib import *
import picamera
import picamera.array
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
    with picamera.PiCamera() as camera:
        with picamera.array.PiRGBArray(camera) as stream:
            camera.resolution = (320, 240)

            while True:
                camera.capture(stream, 'bgr', use_video_port=True)
                # stream.array now contains the image data in BGR order
                #cv2.imshow('frame', stream.array)
                #if cv2.waitKey(1) & 0xFF == ord('q'):
                #    break
                #cv2.imwrite('pic.jpg',stream.array)
                # reset the stream before the next capture
                #stream.seek(0)
                #stream.truncate()
                #yield (b'--frame\r\n'
                    #b'Content-Type: image/jpeg\r\n\r\n' + open('pic.jpg', 'rb').read() + b'\r\n')

#   while True: 
#       rval, frame = vc.read() 
#       cv2.imwrite('pic.jpg', frame) 
#       yield (b'--frame\r\n' 
#          b'Content-Type: image/jpeg\r\n\r\n' + open('pic.jpg', 'rb').read() + b'\r\n') 

@app.route('/video_feed') 
def video_feed(): 
   """Video streaming route. Put this in the src attribute of an img tag.""" 
   return Response(gen(), 
                   mimetype='multipart/x-mixed-replace; boundary=frame') 

if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=80)


#sudo  LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0  python3 server.py

