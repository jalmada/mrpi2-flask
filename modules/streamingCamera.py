import picamera
from .streamingOutput import StreamingOutput
import logging

BLACK_AND_WHITE = (128, 128)

class StreamingCamera:

    def __init__(self, startRecording):
        self.camera = picamera.PiCamera(resolution='720x540', framerate=12)
        self.output = StreamingOutput()
        if(startRecording):
            self.StartRecording()

    def Flip(self, flipX, flipY):
        self.camera.vflip = flipX
        self.camera.hflip = flipY
        
    def StartRecording(self):
        self.camera.start_recording(self.output, format='mjpeg')

    def TakePicture(self, fileName):
        self.camera.capture(f'./captures/{fileName}.jpg')

    def Stream(self):
        try:
            while True:
                with self.output.condition:
                    self.output.condition.wait()
                    frame = self.output.frame
                    yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            logging.warning(e)
    
    def Stop(self):
        self.camera.stop_recording()
        self.camera.close()

    def SetEffects(self, uv):
        self.camera.color_effects = uv

