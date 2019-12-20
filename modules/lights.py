from brightpilib import *

class Lights:

    LED_WHITE_DIM = (2,4,5,7)
    LED_IR_DIM = (1,3,6,8)

    currentLedDim = 0
    currentLedGain = 0

    def __init__(self):
        self.brightPi = BrightPi()
        self.brightPi.reset()

    def Toggle(self, LEDS):
        ledsStatus = self.brightPi.get_led_on_off(LEDS)
        isON = any(led != 0 for led in ledsStatus)
        self.brightPi.set_led_on_off(LEDS, (ON if isON else OFF))
        return isON

    def ToggleDarkMode(self):
        return self.Toggle(LED_IR);
    
    def ToggleLights(self):
        return self.Toggle(LED_WHITE);

    def SetGain(self):
         if (request.method == 'POST'):
            direction = data["direction"]

        if(not direction ):
            gain = data["gain"]

            if(not gain):
                resp = jsonify(success=False)
                resp.status_code = 400
                return resp

            gainNum = int(gain)
            if(gainNum < 0 or gainNum >  BrightPi._max_gain):
                gain = currentGain

            currentGain = gainNum
        else:
            if((currentGain == 0 and direction == 'down') or (currentGain == BrightPi._max_gain and direction == 'up')):
                resp = jsonify(currentGain=currentGain, success=True)
                resp.status_code = 200
                return resp

            if(direction == "up"):
                currentGain = currentGain + 1
            else:
                currentGain = currentGain - 1

        brightPi.set_gain(currentGain)
