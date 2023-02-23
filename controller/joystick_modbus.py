from paho.mqtt import client as mqtt_client
import random
import pygame

# Initialize pygame and the joystick
pygame.init()
pygame.joystick.init()

broker = '10.11.12.77'
port = 1883
client_id = f'python-mqtt-{random.randint(0,1000)}'


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker")
        else:
            print("Failed to connect, return code {rc}")
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


joystick_count = pygame.joystick.get_count()
print(f'[+] {joystick_count} joystick(s) found!')
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Create a Modbus TCP client
client = connect_mqtt()

while True:
    # Poll the joystick for events
    for event in pygame.event.get():
        if event.type == pygame.JOYHATMOTION:
            # Get the joystick axis and value
            print(event.value)
            # Handle joyhatmotion UP event
            if event.value[1] == 1:
                client.publish('joystick/command', 2)
                print('[+] UP Event Handled')
            # Handle joyhatmotion DOWN event
            if event.value[1] == -1:
                client.publish('joystick/command', 8)
                print('[+] DOWN Event Handled')
            # Handle joyhatmotion LEFT event
            if event.value[0] == -1:
                client.publish('joystick/command', 4)
                print('[+] LEFT Event Handled')
            # Handle joyhatmotion RIGHT event
            if event.value[0] == 1:
                client.publish('joystick/command', 6)
                print('[+] RIGHT Event Handled')
            # Handle joyhatmotion NEUTRAL POSITION event
            if event.value == (0,0):
                client.publish('joystick/command', 0)
        elif event.type == pygame.JOYBUTTONDOWN:
            # Handle joyhatmotion RIGHT TRIGGER event
            if event.button == 5:
                client.publish('joystick/command', 6842)
                print('[+] RIGHT TRIGGER Event Handled')
            # Handle joyhatmotion LEFT TRIGGER event
            if event.button == 4:
                client.publish('joystick/command', 6248)
                print('[+] LEFT TRIGGER Event Handled')
        elif event.type == pygame.JOYBUTTONUP:
            client.publish('joystick/command', 0)

