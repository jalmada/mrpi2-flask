import time
from adafruit_servokit import ServoKit

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
try:
	kit = ServoKit(channels=16,address=0x41)
	kit.servo[0].angle = 180
	kit.continuous_servo[1].throttle = 1
	time.sleep(1)
	kit.continuous_servo[1].throttle = -1
	time.sleep(1)
	kit.servo[0].angle = 0
except Exception as e:
	print(e)
