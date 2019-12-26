import RPi.GPIO as GPIO
from time import sleep
import json
import os

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

        self.currentX, self.currentY = GetLastPosition()
        self.Move(self.currentX, self.currentY)

    def SetAngle(self, angleX, angleY):
        if(angleX != self.currentX):
            self.xP.start(0)
            dutyX = self.GetDuty(angleX)
            self.xP.ChangeDutyCycle(dutyX)

        if(angleY != self.currentY):
            self.yP.start(0)
            dutyY = self.GetDuty(angleY)
            self.yP.ChangeDutyCycle(dutyY)

        sleep(1)

        self.xP.ChangeDutyCycle(0)
        self.yP.ChangeDutyCycle(0)
    
    def Step(self, xstep, ystep):
        self.Move(self.currentX + xstep, self.currentY + ystep)
        print(f'Moving: {self.currentX}, {self.currentY}')


    def Move(self, x, y):
        x, y = self.ResolvePosition(x, y)
        
        self.SetAngle(x, y)
        self.currentX = x
        self.currentY = y
        self.SaveLastPosition()

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

    def SaveLastPosition(self):
        data = {}
        data['x'] = self.currentX
        data['y'] = self.currentY
        
        with open('lastpos.json', 'w') as outfile:
            json.dump(data, outfile)
    
    def GetLastPosition(self):
        if os.path.isfile('filename.txt'):
            with open('data.txt') as json_file:
                data = json.load(json_file)
            return data['x'],data['y']
        else: 
            return 0,0
