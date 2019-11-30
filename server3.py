from flask import Flask, jsonify, render_template, Response, request
from brightpilib import *
import picamera
from time import sleep
import io
import logging
from threading import Condition

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


app = Flask(__name__)
brightPi = BrightPi()
brightPi.reset()
camera = picamera.PiCamera()
output = StreamingOutput()
camera.start_recording(output, format='mjpeg')

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/dark', methods=['POST'])
def dark():
    try:
        ledsStaus = brightPi.get_led_on_off(LED_IR)
        isON = not all(led == 0 for led in ledsStaus)
        print(ledsStaus)
        print(isON)
        if(isON):
            brightPi.set_led_on_off(LED_IR, OFF)
        else:
            brightPi.set_led_on_off(LED_IR, ON)

        resp = jsonify(success=True)
        resp.status_code = 200
        return resp
    except Exception as e:
        logging.error(e) 



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

@app.route('/stream.mjpg')
def sendStream():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame') 

def gen():
    try:
        while True:
            with output.condition:
                output.condition.wait()
                frame = output.frame
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except Exception as e:
        logging.warning(e)

if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=80)



