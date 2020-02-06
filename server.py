from flask import Flask, jsonify, render_template, Response, request, stream_with_context
from flask_cors import CORS
import logging
from datetime import datetime
from threading import Lock
#from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
import RPi.GPIO as GPIO

#from modules.servo import Servo
from modules.servoAda import ServoAda
from modules.streamingCamera import *
from modules.audio import Audio
#from modules.lights import Lights

#Servo Pins
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(7, GPIO.OUT)
#GPIO.setup(12, GPIO.OUT)
print(GPIO.getmode())
#Initialize Modules
#servo = Servo(7, 12)
servo = ServoAda(0, 1)
#lights = Lights()
streamingCamera = StreamingCamera(True)
streamingCamera.Flip(True, True)
streamingAudio = Audio()

app = Flask(__name__)
CORS(app)

#Sockets config
async_mode = None
app.config['SECRET_KEY'] = 'secret!'
#socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

@app.route('/')
def index():
    return render_template('index.html') 

#@socketio.on('move', namespace='/servo')
# def moveSocket(message):
#     print(f"Moving to {message}")

#     xstep = message['xstep']
#     ystep = message['ystep']

#     servo.Step(xstep, ystep)
#     emit('my_response', {'data': message})

@app.route('/dark', methods=['POST', 'GET'])
def dark():
    try:
        if (request.method == 'GET'):
            isON = lights.GetDarkModeStatus()
            resp = jsonify(isON=(isON), success=True)
            resp.status_code = 200
            return resp
    
        isON = lights.ToggleDarkMode()
        streamingCamera.SetEffects(BLACK_AND_WHITE if not isON else None)

        resp = jsonify(isON=(not isON), success=True)
        resp.status_code = 200
        return resp
    except Exception as e:
        logging.error(e)

@app.route('/light', methods=['POST','GET'])
def light():
    try:
        if (request.method == 'GET'):
            isON = lights.GetLightModeStatus()
            resp = jsonify(isON=(isON), success=True)
            resp.status_code = 200
            return resp

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


