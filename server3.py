from flask import Flask, jsonify, render_template, Response, request, stream_with_context
from brightpilib import *
import picamera
from time import sleep
import io
import logging
from threading import Condition
from datetime import datetime
import pyaudio
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)

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

LED_WHITE_DIM = (2,4,5,7)
LED_IR_DIM = (1,3,6,8)

app = Flask(__name__)
brightPi = BrightPi()
brightPi.reset()
camera = picamera.PiCamera()
output = StreamingOutput()
camera.start_recording(output, format='mjpeg')
currentLedDim = 0
currentLedGain = 0
audio1 = pyaudio.PyAudio()

FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 44100
CHUNK = 4096
BITS_PER_SAMPLE = 32

def genHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o


wav_header = genHeader(RATE, BITS_PER_SAMPLE, CHANNELS)
stream = audio1.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,input_device_index=2, frames_per_buffer=CHUNK)

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/dark', methods=['POST'])
def dark():
    try:
        ledsStaus = brightPi.get_led_on_off(LED_IR)
        isON = any(led != 0 for led in ledsStaus)
        if(isON):
            brightPi.set_led_on_off(LED_IR, OFF)
        else:
            brightPi.set_led_on_off(LED_IR, ON)

        resp = jsonify(isON=(not isON), success=True)
        resp.status_code = 200
        return resp
    except Exception as e:
        logging.error(e)

@app.route('/light', methods=['POST'])
def light():
    try:
        ledsStaus = brightPi.get_led_on_off(LED_WHITE)
        isON = any(led != 0 for led in ledsStaus)
        if(isON):
            brightPi.set_led_on_off(LED_WHITE, OFF)
        else:
            brightPi.set_led_on_off(LED_WHITE, ON)

        resp = jsonify(isON=(not isON), success=True)
        resp.status_code = 200
        return resp
    except Exception as e:
        logging.error(e) 

@app.route('/gain', methods=['POST','GET'])
def gain():
    data = request.get_json()
    currentGain = brightPi.get_gain()

    if (request.method == 'POST'):
        direction = data["direction"]

        if(not direction ):
            gain = data["gain"]

            if(not gain):
                resp = jsonify(success=False)
                resp.status_code = 400
                return resp

            gainNum = int(gain)
            if(gainNum < 0 or gainNum >  BrightPi._max_gain):
                gain = currentGain

            currentGain = gainNum
        else:
            if((currentGain == 0 and direction == 'down') or (currentGain == BrightPi._max_gain and direction == 'up')):
                resp = jsonify(currentGain=currentGain, success=True)
                resp.status_code = 200
                return resp

            if(direction == "up"):
                currentGain = currentGain + 1
            else:
                currentGain = currentGain - 1

        brightPi.set_gain(currentGain)

    resp = jsonify(currentGain=currentGain, success=True)
    resp.status_code = 200
    return resp

@app.route('/dim', methods=['POST','GET'])
def dim():
    data = request.get_json()
    currentDim = brightPi.get_led_dim()[0]

    if (request.method == 'POST'):
        direction = data["direction"]

        if(not direction ):
            dim = data["dim"]

            if(not dim):
                resp = jsonify(success=False)
                resp.status_code = 400
                return resp

            dimNum = int(dim)
            if(dimNum < 0 or dimNum > BrightPi._max_dim):
                dim = currentDim

            currentDim = dimNum
        else:

            if((currentDim == 0 and direction == 'down') or (currentDim == BrightPi._max_dim and direction == 'up')):
                resp = jsonify(currentDim=currentDim, success=True)
                resp.status_code = 200
                return resp

            if(direction == "up"):
                currentDim = currentDim + 1
            else:
                currentDim = currentDim - 1
     
        brightPi.set_led_dim(LED_WHITE_DIM, currentDim)
        brightPi.set_led_dim(LED_IR_DIM, currentDim)

    resp = jsonify(currentDim=currentDim, success=True)
    resp.status_code = 200
    return resp

@app.route('/photo')
def takePicture():
    today = datetime.now()	
    fileName = today.strftime("%Y-%m-%d-%H_%M_%S")
    camera.capture(f'./captures/{fileName}.jpg')
    resp = jsonify(success=True)
    resp.status_code = 200
    return resp

@app.route('/stream.mjpg')
def sendStream():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame') 

currentServoX = 0
currentServoY = 0

@app.route('/move',  methods=['POST'])
def moveServo():
    data = request.get_json()

    xInc = int(data["x"]) if data["x"] else 0
    yInc = int(data["y"]) if data["y"] else 0

    currentServoX = currentServoX + xInc
    currentServoY = currentServoY + yInc

    currentServoX = 0 if currentServoX < 0 else currentServoX
    currentServoX = 180 if currentServoX > 180 else currentServoX

    currentServoY = 0 if currentServoY < 0 else currentServoY
    currentServoY = 150 if currentServoY > 150 else currentServoY

    SetAngle(currentServoX, currentServoY)
    resp = jsonify(success=True)
    resp.status_code = 200
    return resp

def SetAngle(angle, angle2):
    p.start(0)
    p2.start(0)

    duty = angle/18 + 2.5
    duty2 = angle2/18 + 2.5

	p.ChangeDutyCycle(duty)
	p2.ChangeDutyCycle(duty2)
	sleep(1)
	p.ChangeDutyCycle(0)
	p2.ChangeDutyCycle(0)

    p.stop()
	p2.stop()
	GPIO.cleanup()

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
                
def sound():
    try:
        yield(wav_header)
        while True:
            data = stream.read(CHUNK, exception_on_overflow = False)
            yield (data)
    except Exception as e:
        logging.warning(e)

@app.route('/audio')
def audio():   
    return Response(stream_with_context(sound()))

if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=3000,  threaded=True)



