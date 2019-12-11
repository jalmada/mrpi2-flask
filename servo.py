import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)

p = GPIO.PWM(7, 50)
p2 = GPIO.PWM(12, 43)
p.start(0)
p2.start(0)

def SetAngle(angle, angle2):
	duty = angle/18 + 2.5
	duty2 = angle2/18 + 2.5
	print(f'{duty}:{duty2}:{angle}:{angle2}')
	p.ChangeDutyCycle(duty)
	p2.ChangeDutyCycle(duty2)
	sleep(1)
	p.ChangeDutyCycle(0)
	p2.ChangeDutyCycle(0)

try:
	while True:
		SetAngle(0,0)
		sleep(1.5)
		SetAngle(90, 75)
		sleep(1.5)
		SetAngle(180, 150)
		sleep(1.5)
except KeyboardInterrupt:
	p.stop()
	p2.stop()
	GPIO.cleanup()
