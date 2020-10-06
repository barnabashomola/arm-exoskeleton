#!/usr/bin/env python
from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division

import paho.mqtt.client as mqtt
import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers
from datetime import datetime
# import asyncio
import threading
import logging
import socket
import os

print("Setting up logging...")
logging.basicConfig(filename='exoskeleton.log', filemode="w", format='%(message)s', level=logging.DEBUG)
logging.info("value_wrist,value_elbow,timestamp")
print("Logging is set up!")

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.
BP.set_led(0) # For succesfull setup indication, we turn off the LED and turn it on if it's succesfully set up

print("Setting up UDP connection...")
SERVER_IP = '192.168.0.69'
SERVER_PORT = 5013

CLIENT_IP = "192.168.0.4"
CLIENT_PORT = 5011
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

sock.bind((CLIENT_IP, CLIENT_PORT))
print("UDP connection set up")

print("Sending test UDP message...")
sock.sendto(str.encode("from pi"), (SERVER_IP, SERVER_PORT))

def executeNudging(direction: str):
    if direction == "up":
        target = BP.get_motor_encoder(BP.PORT_C) - 90
        BP.set_motor_position(BP.PORT_C + BP.PORT_A, target)
        # BP.set_motor_power(BP.PORT_C + BP.PORT_A, 100)
        time.sleep(0.5)
        BP.set_motor_power(BP.PORT_C + BP.PORT_A, BP.MOTOR_FLOAT)
    elif direction == "down":
        target = BP.get_motor_encoder(BP.PORT_C) + 90
        BP.set_motor_position(BP.PORT_C + BP.PORT_A, target)
        # BP.set_motor_power(BP.PORT_C + BP.PORT_A, -100)
        time.sleep(0.5)
        BP.set_motor_power(BP.PORT_C + BP.PORT_A, BP.MOTOR_FLOAT)
    elif direction == "left":
        target = BP.get_motor_encoder(BP.PORT_B) + 90
        BP.set_motor_position(BP.PORT_B, target)
        # BP.set_motor_power(BP.PORT_B, 100)
        time.sleep(0.5)
        BP.set_motor_power(BP.PORT_B, BP.MOTOR_FLOAT)
    elif direction == "right":
        target = BP.get_motor_encoder(BP.PORT_B) - 90
        BP.set_motor_position(BP.PORT_B, target)
        # BP.set_motor_power(BP.PORT_B, -100)
        time.sleep(0.5)
        BP.set_motor_power(BP.PORT_B, BP.MOTOR_FLOAT)

def messageCallback(data):
    message = data.decode("utf-8")
    print("Getting message: " + message)

    if message == 'time':
        date_str = str(message.payload.decode("utf-8"))
        print("date:")
        print(date_str)
        os.system('sudo date -s %s' % date_str)
        # os.system('hwclock --set %s' % date_str)

    if message == 'left' or message == 'right' or message == 'up' or message == 'down': 
        actuateThread = threading.Thread(target=executeNudging, args=(message,))
        actuateThread.start()

def main():
    try:
        try:
            BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A))
            BP.offset_motor_encoder(BP.PORT_B, BP.get_motor_encoder(BP.PORT_B))
            BP.offset_motor_encoder(BP.PORT_C, BP.get_motor_encoder(BP.PORT_C))

            # BP.set_motor_limits(BP.PORT_A, 100, 100)
            # BP.set_motor_limits(BP.PORT_B, 100, 100)
            # BP.set_motor_limits(BP.PORT_C, 100, 100)
        except IOError as error:
            print(error)

        BP.set_led(100) # Light up the LED to show the setup is successful
        print("Logging motor value and ready to take nudging messages through UDP...")

        while True:       
            timeStamp = datetime.now().strftime('%H:%M:%S.%f')
            
            value_wrist = float(-BP.get_motor_encoder(BP.PORT_B))
            value_wrist = str(value_wrist)
            value_elbow = (BP.get_motor_encoder(BP.PORT_A) + BP.get_motor_encoder(BP.PORT_C)) * -1 / 2
            value_elbow = str(value_elbow)

            udp_message = str.encode(f"{value_elbow},{value_wrist},{timeStamp}")
            sock.sendto(udp_message, (SERVER_IP, SERVER_PORT))

            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            if (addr[0] == SERVER_IP and data != b''):
                messageCallback(data)

            logging.info(value_wrist + "," + value_elbow + "," + timeStamp)

            time.sleep(0.005) # Without sleep the system logs and sends data to the server ~820 times per second (820 Hz)

    except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
            sock.close()
            print('\nsocket closed')
            logging.info("program stopped")
            BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
            print('program stopped')

if __name__ == "__main__":
    main()