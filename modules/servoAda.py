from adafruit_servokit import ServoKit
import json
import os

class ServoAda:

    servoXMax = 180
    servoYMax = 150

    currentX = -1
    currentY = -1
    currentStepX = 5
    currentStepY = 5

    channels = 16
    address = 0x41

    def __init__(self, xIndex, yIndex):

        self.kit = ServoKit(channels=self.channels,address=self.address)
        self.xIndex = xIndex
        self.yIndex = yIndex

        self.servoX = self.kit.servo[self.xIndex]
        self.servoY = self.kit.servo[self.yIndex]

       
        self.currentX, self.currentY, self.currentStepX, self.currentStepY = self.GetLastPosition()
        self.Move(self.currentX, self.currentY)

    def SetAngle(self, angleX, angleY):
        if(angleX != self.currentX):
            self.servoX.angle = angleX

        if(angleY != self.currentY):
            self.servoY.angle = angleY
    
    def Step(self, xstep = None, ystep = None):

        if(xstep is not None):
            self.currentStepX = xstep

        if(ystep is not None):
            self.currentStepY = ystep

        self.Move(self.currentX + self.currentStepX, self.currentY + self.currentStepY)
        print(f'Moving: {self.currentX}, {self.currentY}')


    def Move(self, x, y):
        x, y = self.ResolvePosition(x, y)
        
        self.SetAngle(x, y)
        self.currentX = x
        self.currentY = y
        self.SaveLastPosition()

    def ResolvePosition(self, x, y):
        newX = 0 if x < 0 else x
        newX = 180 if x > 180 else x

        newY = 0 if y < 0 else y
        newY = 150 if y > 150 else y

        return newX, newY

    def SaveLastPosition(self):
        data = {}
        data['x'] = self.currentX
        data['y'] = self.currentY
        data['stepX'] = self.currentStepX
        data['stepY'] = self.currentStepY
        
        with open('lastpos.json', 'w') as outfile:
            json.dump(data, outfile)
    
    def GetLastPosition(self):
        if os.path.isfile('lastpos.json'):
            with open('lastpos.json') as json_file:
                data = json.load(json_file)
                stepX = self.currentStepX if 'stepX' in not data else data['stepX']
                stepY = self.currentStepY if 'stepY' in not data else data['stepY']

            return data['x'],data['y'], stepX, stepY
        else: 
            return 0,0
