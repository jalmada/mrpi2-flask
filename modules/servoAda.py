from adafruit_servokit import ServoKit
import json
import os

class ServoAda:

    servoXMax = 180
    servoYMax = 150

    currentX = -1
    currentY = -1

    channels = 16
    address = 0x41

    def __init__(self, xIndex, yIndex):

        self.kit = ServoKit(channels=self.channels,address=self.address)
        self.xIndex = xIndex
        self.yIndex = yIndex

        self.servoX = self.kit.servo[self.xIndex]
        self.servoY = self.kit.servo[self.yIndex]

       
        self.currentX, self.currentY = self.GetLastPosition()
        self.Move(self.currentX, self.currentY)

    def SetAngle(self, angleX, angleY):
        if(angleX != self.currentX):
            self.servoX = angleX

        if(angleY != self.currentY):
            self.servoY = angleY
    
    def Step(self, xstep, ystep):
        self.Move(self.currentX + xstep, self.currentY + ystep)
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
        
        with open('lastpos.json', 'w') as outfile:
            json.dump(data, outfile)
    
    def GetLastPosition(self):
        if os.path.isfile('filename.txt'):
            with open('data.txt') as json_file:
                data = json.load(json_file)
            return data['x'],data['y']
        else: 
            return 0,0
