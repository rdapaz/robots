from PiicoDev_VL53L1X import PiicoDev_VL53L1X
from PiicoDev_LIS3DH import PiicoDev_LIS3DH
from PiicoDev_SSD1306 import *
from PiicoDev_Unified import sleep_ms

import machine
import utime
import network
import socket

ssid = 'ProdWireless'
password = 'CiscoRul3s'

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    print(wlan.ifconfig())


class MotorDriver():
    def __init__(self,M1A,M1B,M2A,M2B):
        
        self.M1A = machine.PWM(machine.Pin(M1A))
        self.M1B = machine.PWM(machine.Pin(M1B))
        self.M2A = machine.PWM(machine.Pin(M2A))
        self.M2B = machine.PWM(machine.Pin(M2B))
    
    # Will return a integer
    def convert(self,x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def speed(self,speedLeft, speedRight):
        speedLeft = self.convert(speedLeft,0,100,0,65534)
        speedRight = self.convert(speedRight,0,100,0,65534)
        if speedLeft > 0:
            self.M1A.duty_u16(speedLeft)
            self.M1B.duty_u16(0)
        else:
            self.M1A.duty_u16(0)
            self.M1B.duty_u16(abs(speedLeft))

        if speedRight > 0:
            self.M2A.duty_u16(speedRight)
            self.M2B.duty_u16(0)
        else:
            self.M2A.duty_u16(0)
            self.M2B.duty_u16(abs(speedRight))
            
    def brake(self):
        self.speed(0,0)

Front = MotorDriver(1,2,4,5)
Back = MotorDriver(11,12,14,15)

def StraightAhead(s):
    Front.speed(s,s)
    Back.speed(s,s)
    
def StraightReverse(s):
    Front.speed(-s,-s)
    Back.speed(-s,-s)

def StraightLeft(s):
    Front.speed(-s,s)
    Back.speed(s,-s)

def StraightRight(s):
    Front.speed(s,-s)
    Back.speed(-s,s)

def DiagFwdLeft(s):
    Front.speed(0,s)
    Back.speed(s,0)

def DiagFwdRight(s):
    Front.speed(s,0)
    Back.speed(0,s)

def DiagRevLeft(s):
    Front.speed(-s,0)
    Back.speed(0,-s)

def DiagRevRight(s):
    Front.speed(0,-s)
    Back.speed(-s, 0)


distSensor = PiicoDev_VL53L1X()
motion = PiicoDev_LIS3DH() # Initialise the accelerometer
display = create_PiicoDev_SSD1306()

motion.range = 2 # Set the range to +-2g

while True:
    try:
        connect()
    except KeyboardInterrupt:
        machine.reset()
    print('[+] Successfully connected!')
    dist = distSensor.read() 
    st_out1 = f"{dist} mm"
    print(str(dist) + " mm")
    
    x, y, z = motion.acceleration
    x = round(x,2) 
    y = round(y,2)
    z = round(z,2)
    
    st_out2 = f"x={x}"
    st_out3 = f"y={y}"
    st_out4 = f"z={z}"
    display.fill(0)
    display.text(st_out1,30,5,1)
    display.text(st_out2,30,15,1) 
    display.text(st_out3,30,25,1) 
    display.text(st_out4,30,35,1) 
    display.show()
    sleep_ms(500)


