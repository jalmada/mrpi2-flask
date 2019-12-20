from flask import Flask, jsonify, Response, request, stream_with_context
from datetime import datetime

def takePicture(streamingCamera):
    today = datetime.now()	
    fileName = today.strftime("%Y-%m-%d-%H_%M_%S")

    streamingCamera.TakePicture(fileName)

    resp = jsonify(success=True)
    resp.status_code = 200
    return resp


def sendStream(streamingCamera):
    return Response(streamingCamera.Stream(), mimetype='multipart/x-mixed-replace; boundary=frame') 