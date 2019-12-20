from brightpilib import *

class Lights:

    LED_WHITE_DIM = (2,4,5,7)
    LED_IR_DIM = (1,3,6,8)

    def __init__(self):
        self.brightPi = BrightPi()
        self.brightPi.reset()

    def Toggle(self, LEDS):
        ledsStatus = self.brightPi.get_led_on_off(LEDS)
        isON = any(led != 0 for led in ledsStatus)
        self.brightPi.set_led_on_off(LEDS, (ON if isON else OFF))
        return isON

    def ToggleDarkMode(self):
        return self.Toggle(LED_IR)
    
    def ToggleLights(self):
        return self.Toggle(LED_WHITE)

    def StepGain(self, step):
        currentGain = self.brightPi.get_gain()
        newGain = currentGain + step

        currentGain = newGain if newGain >= 0 else 0
        currentGain = newGain if newGain <= BrightPi._max_gain else BrightPi._max_gain

        self.brightPi.set_gain(currentGain)
        return currentGain

    def SetGain(self, gain):
        currentGain = self.brightPi.get_gain()
        if(gain < 0):
            currentGain = 0
        else if (gain > BrightPi._max_gain):
            currentGain = BrightPi._max_gain
        else:
            currentGain = gain

        self.brightPi.set_gain(currentGain)
        return currentGain

    def GetGain(self):
        return self.brightPi.get_gain()

    def StepDim(self, step):
        currentDim = self.brightPi.get_led_dim()[0]

        newDim = currentDim + step

        currentDim = newDim if newDim >= 0 else 0
        currentDim = newDim if newDim <= BrightPi._max_dim else BrightPi._max_dim

        self.brightPi.set_led_dim(self.LED_WHITE_DIM, currentDim)
        self.brightPi.set_led_dim(self.LED_IR_DIM, currentDim)
        return currentDim

    def SetDim(self, dim):
        currentDim = self.brightPi.get_led_dim()[0]

        if(dim < 0):
            currentDim = 0
        else if (dim > BrightPi._max_dim):
            currentDim = BrightPi._max_dim
        else:
            currentDim = dim

        self.brightPi.set_led_dim(self.LED_WHITE_DIM, currentDim)
        self.brightPi.set_led_dim(self.LED_IR_DIM, currentDim)
        return currentDim

    def GetDim(self):
        return self.brightPi.get_led_dim()[0]

