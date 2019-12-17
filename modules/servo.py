import RPi.GPIO as GPIO
from time import sleep

class Servo:

    servoXMax = 180
    servoYMax = 150

    currentX = 0
    currentY = 0

    def __init__(self, xPin, yPin):
        self.xPin = xPin
        self.yPin = yPin

        self.xP = GPIO.PWM(xPin, 50)
        self.yP = GPIO.PWM(yPin, 43)    

    def SetAngle(self, angleX, angleY):
        self.xP.start(0)
        self.yP.start(0)

        dutyX = self.GetDuty(angleX)
        dutyY = self.GetDuty(angleY)

        self.xP.ChangeDutyCycle(dutyX)
        self.yP.ChangeDutyCycle(dutyY)
        sleep(1)
        self.xP.ChangeDutyCycle(0)
        self.yP.ChangeDutyCycle(0)
    
    def Move(self, x, y):
        x, y = self.ResolvePosition(x, y)
        self.SetAngle(x, y)
        currentX = x
        currentY = y

    def GetDuty(self, angle):
        return angle/18 + 2.5

    def ResolvePosition(self, x, y):
        newX = 0 if x < 0 else x
        newX = 180 if x > 180 else x

        newY = 0 if y < 0 else y
        newY = 150 if y > 150 else y

        return newX, newY

    def Stop(self):
        self.xP.stop()
        self.yP.stop()
