from flask import Flask, jsonify, render_template, Response, request, stream_with_context
import logging
from datetime import datetime
import RPi.GPIO as GPIO

from modules.servo import Servo
from modules.streamingCamera import StreamingCamera
from modules.audio import Audio
from modules.lights import Lights

#Servo Pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)

#Initialize Modules
servo = Servo(7, 12)
lights = Lights()
streamingCamera = StreamingCamera(True)
streamingCamera.Flip(True, True)
streamingAudio = Audio()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/dark', methods=['POST'])
def dark():
    try:
        isON = lights.ToggleDarkMode()

        resp = jsonify(isON=(not isON), success=True)
        resp.status_code = 200
        return resp
    except Exception as e:
        logging.error(e)

@app.route('/light', methods=['POST'])
def light():
    try:
        isON = lights.ToggleLights()

        resp = jsonify(isON=(not isON), success=True)
        resp.status_code = 200
        return resp
    except Exception as e:
        logging.error(e) 

@app.route('/gain', methods=['POST','GET'])
def gain():
    step = 5
    data = request.get_json()
    currentGain = lights.GetGain()

    if (request.method == 'POST'):

        if (data["gain"]):
            currentGain = lights.SetGain(int(data["gain"]))
        elif (data["direction"]):
            multi = -1 if data["direction"] == 'down' else 1
            currentGain = lights.StepGain(step * multi)
        else:
            resp = jsonify(success=False)
            resp.status_code = 400
            return resp

    resp = jsonify(currentGain=currentGain, success=True)
    resp.status_code = 200
    return resp

@app.route('/dim', methods=['POST','GET'])
def dim():
    step = 5
    data = request.get_json()
    currentDim = lights.GetDim()

    if (request.method == 'POST'):

        if (data["dim"]):
            currentDim = lights.SetDim(int(data["dim"]))
        elif (data["direction"]):
            multi = -1 if data["direction"] == 'down' else 1
            currentDim = lights.StepDim(step * multi)
        else:
            resp = jsonify(success=False)
            resp.status_code = 400
            return resp

    resp = jsonify(currentDim=currentDim, success=True)
    resp.status_code = 200
    return resp

@app.route('/move',  methods=['POST'])
def moveServo():
    data = request.get_json()
    currentServoX = int(data["x"]) if data["x"] else 0
    currentServoY = int(data["y"]) if data["y"] else 0

    servo.Move(currentServoX, currentServoY)

    resp = jsonify(success=True)
    resp.status_code = 200
    return resp

@app.route('/photo')
def photo():
    today = datetime.now()	
    fileName = today.strftime("%Y-%m-%d-%H_%M_%S")

    streamingCamera.TakePicture(fileName)

    resp = jsonify(success=True)
    resp.status_code = 200
    return resp

@app.route('/stream.mjpg')
def stream():
    return Response(streamingCamera.Stream(), mimetype='multipart/x-mixed-replace; boundary=frame') 

@app.route('/audio')
def audio():   
    return Response(stream_with_context(streamingAudio.sound()))

if (__name__ == '__main__'):
    try:
        app.run(host='0.0.0.0', port=3000,  threaded=True)
    except Exception as e:
        servo.Stop()
        streamingCamera.Stop()
        GPIO.cleanup()


