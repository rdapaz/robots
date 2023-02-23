from PiicoDev_VL53L1X import PiicoDev_VL53L1X
from PiicoDev_LIS3DH import PiicoDev_LIS3DH
from PiicoDev_SSD1306 import *
from PiicoDev_Unified import sleep_ms
from mqttsimple import MQTTClient

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
        sleep_ms(1000)
    return wlan.ifconfig()


class MotorDriver():
    def __init__(self,M1A,M2A,M1B,M2B):
        
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


class MotorControl():
    def __init__(self, Front_M1A,Front_M1B,Front_M2A,Front_M2B,\
                 Rear_M1A,Rear_M1B,Rear_M2A,Rear_M2B):
        self.Front = MotorDriver(Front_M1A,Front_M1B,Front_M2A,Front_M2B)
        self.Back = MotorDriver(Rear_M1A,Rear_M1B,Rear_M2A,Rear_M2B)
        self.speed = 100

    def StraightAhead(self):
        self.Front.speed(self.speed,self.speed)
        self.Back.speed(self.speed,self.speed)
    
    def StraightReverse(self):
        self.Front.speed(-self.speed,-self.speed)
        self.Back.speed(-self.speed,-self.speed)

    def StraightLeft(self):
        self.Front.speed(-self.speed,self.speed)
        self.Back.speed(self.speed,-self.speed)

    def StraightRight(self):
        self.Front.speed(self.speed,-self.speed)
        self.Back.speed(-self.speed,self.speed)

    def DiagFwdLeft(self):
        self.Front.speed(0,self.speed)
        self.Back.speed(self.speed,0)

    def DiagFwdRight(self):
        self.Front.speed(self.speed,0)
        self.Back.speed(0,self.speed)

    def DiagRevLeft(self):
        self.Front.speed(-self.speed,0)
        self.Back.speed(0,-self.speed)

    def DiagRevRight(self):
        self.Front.speed(0,-self.speed)
        self.Back.speed(-self.speed, 0)
        
    def Halt(self):
        self.Front.brake()
        self.Back.brake()


joystick_command = ''
distSensor = PiicoDev_VL53L1X()
motion = PiicoDev_LIS3DH() # Initialise the accelerometer
display = create_PiicoDev_SSD1306()

motion.range = 2 # Set the range to +-2g
connected = False


# Set up MQTT client
client = MQTTClient(client_id="pico", server="10.11.12.77")

# Define callback function for incoming messages
def message_callback(topic, msg):
    global joystick_command
    joystick_command = msg

# Define a delay in microseconds (here, we use a 5-second delay)
delay_us = 5000000
delay_2s = 2000000


# Get the current time in microseconds
start_time = utime.ticks_us()
ips = connect()

# Wait for the specified delay
while utime.ticks_diff(utime.ticks_us(), start_time) < delay_us:
    pass

# Connect to MQTT broker and subscribe to desired topics
client.connect()
client.set_callback(message_callback)
client.subscribe('joystick/command')

# Listen for incoming messages and display topic in console

while True:
    # ips = connect()
    dist = distSensor.read() 
    print(str(dist) + " mm")
    
    client.check_msg()
    x, y, z = motion.acceleration
    x = round(x,2) 
    y = round(y,2)
    z = round(z,2)

    controller = MotorControl(4,5,9,10,14,15,19,20)
         
    st_out1 = f"{dist} mm"    
    st_out2 = f"x={x}"
    st_out3 = f"y={y}"
    st_out4 = f"z={z}"
    
    display.fill(0)
    display.text(st_out1,30,5,1)
    display.text(st_out2,30,15,1) 
    display.text(st_out3,30,25,1) 
    display.text(st_out4,30,35,1)
    # display.text(ips[0],30,45,1)
    display.text(joystick_command,30,45,1)
    action_display = lambda x: display.text(x,30,45,1)
    print(joystick_command)
    if dist >= 40:
        if joystick_command == b'2':
            action_display('Forward')
            controller.StraightAhead()
        elif joystick_command == b'8':
            action_display('Backward')
            controller.StraightReverse()
        elif joystick_command == b'4':
            action_display('Left')
            controller.StraightLeft()
        elif(joystick_command) == b'6':
             action_display('Right')
             controller.StraightRight()
        elif(joystick_command) == b'6248':
            action_display('DiagFwdLft')
            controller.DiagFwdLeft()
        elif(joystick_command) == b'6842':
            action_display('DiagFwdRgt')
            controller.DiagFwdRight()
        elif(joystick_command) == b'0':
            action_display('Neutral')
            controller.Halt()
    else:
        controller.Halt()
        action_display('Panic!')
        stt1 = utime.tick_us()
        while utime.tick_us() - stt1 < delay_2s:
            controller.StraightReverse()
        
    display.show()
    sleep_ms(500)

