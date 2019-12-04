from flask import Flask, jsonify, render_template, Response, request
from brightpilib import *
import picamera
from time import sleep
import io
import logging
from threading import Condition
from datetime import datetime
#import pyaudio

# FORMAT = pyaudio.paInt16
# CHANNELS = 2
# RATE = 44100
# CHUNK = 1024
# RECORD_SECONDS = 5

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
currentLedDim = 0
currentLedGain = 0
#audio1 = pyaudio.PyAudio()

# def genHeader(sampleRate, bitsPerSample, channels):
#     datasize = 2000*10**6
#     o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
#     o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
#     o += bytes("WAVE",'ascii')                                              # (4byte) File type
#     o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
#     o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
#     o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
#     o += (channels).to_bytes(2,'little')                                    # (2byte)
#     o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
#     o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
#     o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
#     o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
#     o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
#     o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
#     return o


@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/dark', methods=['POST'])
def dark():
    try:
        ledsStaus = brightPi.get_led_on_off(LED_IR)
        isON = not all(led == 0 for led in ledsStaus)
        if(isON):
            brightPi.set_led_on_off(LED_IR, OFF)
        else:
            brightPi.set_led_on_off(LED_IR, ON)

        resp = jsonify(success=True)
        resp.status_code = 200
        return resp
    except Exception as e:
        logging.error(e) 

@app.route('/setGain', methods=['POST'])
def setGain():
    data = request.get_json()
    logging.error(data.gain)    
    brightPi.set_gain(data.gain)

@app.route('/setDim', methods=['POST'])
def setGain(dim):
    data = request.get_json()
    logging.error(data.dim)    
    brightPi.set_led_dim(LED_IR, data.dim)



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

# @app.route('/audio')
# def audio():
#     # start Recording
#     def sound():

#         CHUNK = 1024
#         sampleRate = 44100
#         bitsPerSample = 16
#         channels = 2
#         wav_header = genHeader(sampleRate, bitsPerSample, channels)

#         stream = audio1.open(format=FORMAT, channels=CHANNELS,
#                         rate=RATE, input=True,input_device_index=1,
#                         frames_per_buffer=CHUNK)
#         print("recording...")
#         #frames = []

#         while True:
#             data = wav_header+stream.read(CHUNK)
#             yield(data)

#     return Response(sound())



if (__name__ == '__main__'):
    app.run(host='0.0.0.0', port=80)



