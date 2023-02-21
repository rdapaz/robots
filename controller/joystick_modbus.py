import pygame
import pymodbus
from pymodbus.client import ModbusTcpClient

# Initialize pygame and the joystick
pygame.init()
pygame.joystick.init()

joystick_count = pygame.joystick.get_count()
print(f'[+] {joystick_count} joystick(s) found!')
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Create a Modbus TCP client
client = ModbusTcpClient('localhost')
client.connect()
while True:
    # Poll the joystick for events
    for event in pygame.event.get():
        if event.type == pygame.JOYHATMOTION:
            # Get the joystick axis and value
            print(event.value)
            # Handle joyhatmotion UP event
            if event.value[1] == 1:
                client.write_registers(0x1, 2)
                print('[+] UP Event Handled')
            # Handle joyhatmotion DOWN event
            if event.value[1] == -1:
                client.write_registers(0x1, 8)
                print('[+] DOWN Event Handled')
            # Handle joyhatmotion LEFT event
            if event.value[0] == -1:
                client.write_registers(0x1, 4)
                print('[+] LEFT Event Handled')
            # Handle joyhatmotion RIGHT event
            if event.value[0] == 1:
                client.write_registers(0x1, 6)
                print('[+] RIGHT Event Handled')
            # Handle joyhatmotion NEUTRAL POSITION event
            if event.value == (0,0):
                client.write_registers(0x1, 0)
        elif event.type == pygame.JOYBUTTONDOWN:
            # Handle joyhatmotion RIGHT TRIGGER event
            if event.button == 5:
                client.write_registers(0x1, 6842)
                print('[+] RIGHT TRIGGER Event Handled')
            # Handle joyhatmotion LEFT TRIGGER event
            if event.button == 4:
                client.write_registers(0x1, 6248)
                print('[+] LEFT TRIGGER Event Handled')
        elif event.type == pygame.JOYBUTTONUP:
            client.write_registers(0x1, 0)
# Close the Modbus TCP client when the program is finished
client.close()
