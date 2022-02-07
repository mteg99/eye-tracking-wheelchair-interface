# Python Script
# https://www.electronicshub.org/raspberry-pi-l298n-interface-tutorial-control-dc-motor-l298n-raspberry-pi/

import RPi.GPIO as GPIO          
from time import sleep

backRight1 = 23  # Back Right
backRight2 = 24
backRightEnable = 25

frontLeft1 = 12  # Front Left
frontLeft2 = 16
frontLeftEnable = 26

backLeft1 = 6  # Back Left
backLeft2 = 13
backLeftEnable = 5

frontRight1 = 22  # Front Right
frontRight2 = 27
frontRightEnable = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(backRight1,GPIO.OUT)
GPIO.setup(backRight2,GPIO.OUT)

GPIO.setup(frontLeft1,GPIO.OUT)
GPIO.setup(frontLeft2,GPIO.OUT)

GPIO.setup(backLeft1,GPIO.OUT)
GPIO.setup(backLeft2,GPIO.OUT)

GPIO.setup(frontRight1,GPIO.OUT)
GPIO.setup(frontRight2,GPIO.OUT)

GPIO.setup(backRightEnable,GPIO.OUT)
GPIO.setup(frontLeftEnable,GPIO.OUT)
GPIO.setup(backLeftEnable,GPIO.OUT)
GPIO.setup(frontRightEnable,GPIO.OUT)

GPIO.output(backRight1,GPIO.LOW)
GPIO.output(backRight2,GPIO.LOW)

GPIO.output(frontLeft1,GPIO.LOW)
GPIO.output(frontLeft2,GPIO.LOW)

GPIO.output(backLeft1,GPIO.LOW)
GPIO.output(backLeft2,GPIO.LOW)

GPIO.output(frontRight1,GPIO.LOW)
GPIO.output(frontRight2,GPIO.LOW)

p=GPIO.PWM(backRightEnable,1000)
p2=GPIO.PWM(frontLeftEnable,1000)
p3=GPIO.PWM(backLeftEnable,1000)
p4=GPIO.PWM(frontRightEnable,1000)

p.start(50)
p2.start(50)
p3.start(50)
p4.start(50)
print("\n")
print("The default speed & direction of motor is LOW & Forward.....")
print("s-stop f-forward b-backward r-right l-left low-low med-medium high-high e-exit")
print("\n")    

while(1):

    x=input()

    if x=='s':
        print("stop")
        GPIO.output(backRight1,GPIO.LOW)
        GPIO.output(backRight2,GPIO.LOW)
        GPIO.output(frontLeft1,GPIO.LOW)
        GPIO.output(frontLeft2,GPIO.LOW)
        GPIO.output(backLeft1,GPIO.LOW)
        GPIO.output(backLeft2,GPIO.LOW)
        GPIO.output(frontRight1,GPIO.LOW)
        GPIO.output(frontRight2,GPIO.LOW)
        x='z'

    elif x=='f':
        print("forward")
        GPIO.output(backRight1,GPIO.HIGH)
        GPIO.output(backRight2,GPIO.LOW)
        GPIO.output(frontLeft1,GPIO.HIGH)
        GPIO.output(frontLeft2,GPIO.LOW)
        GPIO.output(backLeft1,GPIO.HIGH)
        GPIO.output(backLeft2,GPIO.LOW)
        GPIO.output(frontRight1,GPIO.HIGH)
        GPIO.output(frontRight2,GPIO.LOW)
        x='z'

    elif x=='b':
        print("backward")
        GPIO.output(backRight1,GPIO.LOW)
        GPIO.output(backRight2,GPIO.HIGH)
        GPIO.output(frontLeft1,GPIO.LOW)
        GPIO.output(frontLeft2,GPIO.HIGH)
        GPIO.output(backLeft1,GPIO.LOW)
        GPIO.output(backLeft2,GPIO.HIGH)
        GPIO.output(frontRight1,GPIO.LOW)
        GPIO.output(frontRight2,GPIO.HIGH)
        x='z'
    
    elif x=='r':
        print('right')
        GPIO.output(backRight1,GPIO.LOW)
        GPIO.output(backRight2,GPIO.HIGH)
        GPIO.output(frontLeft1,GPIO.HIGH)
        GPIO.output(frontLeft2,GPIO.LOW)
        GPIO.output(backLeft1,GPIO.HIGH)
        GPIO.output(backLeft2,GPIO.LOW)
        GPIO.output(frontRight1,GPIO.LOW)
        GPIO.output(frontRight2,GPIO.HIGH)
        x='z'

    elif x=='l':
        print('left')
        GPIO.output(backRight1,GPIO.HIGH)
        GPIO.output(backRight2,GPIO.LOW)
        GPIO.output(frontLeft1,GPIO.LOW)
        GPIO.output(frontLeft2,GPIO.HIGH)
        GPIO.output(backLeft1,GPIO.LOW)
        GPIO.output(backLeft2,GPIO.HIGH)
        GPIO.output(frontRight1,GPIO.HIGH)
        GPIO.output(frontRight2,GPIO.LOW)
        x='z'

    elif x=='low':
        print("low")
        p.ChangeDutyCycle(25)
        p2.ChangeDutyCycle(25)
        p3.ChangeDutyCycle(25)
        p4.ChangeDutyCycle(25)
        x='z'

    elif x=='med':
        print("medium")
        p.ChangeDutyCycle(50)
        p2.ChangeDutyCycle(50)
        p3.ChangeDutyCycle(50)
        p4.ChangeDutyCycle(50)
        x='z'

    elif x=='high':
        print("high")
        p.ChangeDutyCycle(75)
        p2.ChangeDutyCycle(75)
        p3.ChangeDutyCycle(75)
        p4.ChangeDutyCycle(75)
        x='z'
     
    
    elif x=='e':
        GPIO.cleanup()
        print("GPIO Clean up")
        break
    
    else:
        print("<<<  wrong data  >>>")
        print("please enter the defined data to continue.....")

