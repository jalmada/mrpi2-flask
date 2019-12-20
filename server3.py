from flask import Flask, jsonify, render_template, Response, request, stream_with_context
from brightpilib import *
import logging
# from datetime import datetime
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

# LED_WHITE_DIM = (2,4,5,7)
# LED_IR_DIM = (1,3,6,8)

app = Flask(__name__)
# brightPi = BrightPi()
# brightPi.reset()
# currentLedDim = 0
# currentLedGain = 0

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/dark', methods=['POST'])
def dark():
    try:
        # ledsStaus = brightPi.get_led_on_off(LED_IR)
        # isON = any(led != 0 for led in ledsStaus)
        # if(isON):
        #     brightPi.set_led_on_off(LED_IR, OFF)
        # else:
        #     brightPi.set_led_on_off(LED_IR, ON)

        
        isON = lights.ToggleDarkMode()

        resp = jsonify(isON=(not isON), success=True)
        resp.status_code = 200
        return resp
    except Exception as e:
        logging.error(e)

@app.route('/light', methods=['POST'])
def light():
    try:
        # ledsStaus = brightPi.get_led_on_off(LED_WHITE)
        # isON = any(led != 0 for led in ledsStaus)
        # if(isON):
        #     brightPi.set_led_on_off(LED_WHITE, OFF)
        # else:
        #     brightPi.set_led_on_off(LED_WHITE, ON)

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

    # currentGain = brightPi.get_gain()

    if (request.method == 'POST'):

        direction = data["direction"] if data["direction"] else False
        gain = data["gain"] if data["gain"] else False

        if(gain):
            currentGain = lights.SetGain(int(gain))
        elif (direction):
            multi = -1 if direction == 'down' else 1
            currentGain = lights.SetGain(step * multi)
        else:
            resp = jsonify(success=False)
            resp.status_code = 400
            return resp

    resp = jsonify(currentGain=currentGain, success=True)
    resp.status_code = 200
    return resp


        # if(not direction ):
        #     gain = data["gain"]

        #     if(not gain):
        #         resp = jsonify(success=False)
        #         resp.status_code = 400
        #         return resp

            # gainNum = int(gain)
            # if(gainNum < 0 or gainNum >  BrightPi._max_gain):
            #     gain = currentGain

            #currentGain = gainNum
    #     else:
    #         if((currentGain == 0 and direction == 'down') or (currentGain == BrightPi._max_gain and direction == 'up')):
    #             resp = jsonify(currentGain=currentGain, success=True)
    #             resp.status_code = 200
    #             return resp

    #         if(direction == "up"):
    #             currentGain = currentGain + 1
    #         else:
    #             currentGain = currentGain - 1

    #     brightPi.set_gain(currentGain)

    # resp = jsonify(currentGain=currentGain, success=True)
    # resp.status_code = 200
    # return resp

@app.route('/dim', methods=['POST','GET'])
def dim():
    data = request.get_json()
    currentDim = lights.GetDim()

    if (request.method == 'POST'):

        direction = data["direction"] if data["direction"] else False
        dim = data["dim"] if data["dim"] else False

        if(dim):
            currentDim = lights.SetDim(int(dim))
        elif (direction):
            multi = -1 if direction == 'down' else 1
            currentDim = lights.SetDim(step * multi)
        else:
            resp = jsonify(success=False)
            resp.status_code = 400
            return resp

    resp = jsonify(currentDim=currentDim, success=True)
    resp.status_code = 200
    return resp
    # data = request.get_json()
    # currentDim = brightPi.get_led_dim()[0]

    # if (request.method == 'POST'):
    #     direction = data["direction"]

    #     if(not direction ):
    #         dim = data["dim"]

    #         if(not dim):
    #             resp = jsonify(success=False)
    #             resp.status_code = 400
    #             return resp

    #         dimNum = int(dim)
    #         if(dimNum < 0 or dimNum > BrightPi._max_dim):
    #             dim = currentDim

    #         currentDim = dimNum
    #     else:

    #         if((currentDim == 0 and direction == 'down') or (currentDim == BrightPi._max_dim and direction == 'up')):
    #             resp = jsonify(currentDim=currentDim, success=True)
    #             resp.status_code = 200
    #             return resp

    #         if(direction == "up"):
    #             currentDim = currentDim + 1
    #         else:
    #             currentDim = currentDim - 1
     
    #     brightPi.set_led_dim(LED_WHITE_DIM, currentDim)
    #     brightPi.set_led_dim(LED_IR_DIM, currentDim)

    # resp = jsonify(currentDim=currentDim, success=True)
    # resp.status_code = 200
    # return resp

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
def takePicture():
    today = datetime.now()	
    fileName = today.strftime("%Y-%m-%d-%H_%M_%S")

    streamingCamera.TakePicture(fileName)

    resp = jsonify(success=True)
    resp.status_code = 200
    return resp

@app.route('/stream.mjpg')
def sendStream():
    return Response(streamingCamera.Stream(), mimetype='multipart/x-mixed-replace; boundary=frame') 

@app.route('/audio')
def audio():   
    return Response(stream_with_context(streamingAudio.sound()))

if (__name__ == '__main__'):
    try:
        app.run(host='0.0.0.0', port=3000,  threaded=True)
    except Exception as e:
        servo.Stop()
        GPIO.cleanup()


