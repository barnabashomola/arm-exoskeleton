#!/usr/bin/env python
from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division

import paho.mqtt.client as mqtt
import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers
from datetime import datetime
import logging
import os

print("Setting up MQTT...")

client = mqtt.Client("raspi_controller")
client.connect("192.168.0.6")
# client.connect("172.20.10.2")
# client.connect("192.168.0.100")

logging.basicConfig(filename='exoskeleton.log', filemode="w", format='%(message)s', level=logging.DEBUG)
logging.info("value_wrist,value_elbow,timestamp")

client.publish("test", "initial_test_message")

print("Initial MQTT test message sent")

print("Subscribing to nudging topic..")

#client.subscribe("motor_command_wrist")
#client.subscribe("motor_command_elbow")
client.subscribe("nudge", qos=1)
client.subscribe("time", qos=1)

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

holdMqtt = False

def messageCallback(client, userdata, message):
    print("Getting message on topic: " + str(message.topic))
    if str(message.topic)== "time":
        date_str = str(message.payload.decode("utf-8"))
        print("date:")
        print(date_str)
        os.system('sudo date -s %s' % date_str)
        # os.system('hwclock --set %s' % date_str)

    if str(message.topic)== "motor_command_wrist":
        message = str(message.payload.decode("utf-8"))
        BP.set_motor_power(BP.PORT_C, int(message))

    if str(message.topic)== "motor_command_elbow":
        message = str(message.payload.decode("utf-8"))
        BP.set_motor_power(BP.PORT_B, int(message))

    if str(message.topic)== "nudge":
        holdMqtt = True

        message = str(message.payload.decode("utf-8"))
        print(message)
        if message == "up":
            target = BP.get_motor_encoder(BP.PORT_C) - 100
            BP.set_motor_position(BP.PORT_C + BP.PORT_A, target)
            # BP.set_motor_power(BP.PORT_C + BP.PORT_A, 100)
            time.sleep(0.5)
            BP.set_motor_power(BP.PORT_C + BP.PORT_A, BP.MOTOR_FLOAT)
        elif message == "down":
            target = BP.get_motor_encoder(BP.PORT_C) + 100
            BP.set_motor_position(BP.PORT_C + BP.PORT_A, target)
            # BP.set_motor_power(BP.PORT_C + BP.PORT_A, -100)
            time.sleep(0.5)
            BP.set_motor_power(BP.PORT_C + BP.PORT_A, BP.MOTOR_FLOAT)
        elif message == "left":
            target = BP.get_motor_encoder(BP.PORT_B) + 100
            BP.set_motor_position(BP.PORT_B, target)
            # BP.set_motor_power(BP.PORT_B, 100)
            time.sleep(0.5)
            BP.set_motor_power(BP.PORT_B, BP.MOTOR_FLOAT)
        elif message == "right":
            target = BP.get_motor_encoder(BP.PORT_B) - 100
            BP.set_motor_position(BP.PORT_B, target)
            # BP.set_motor_power(BP.PORT_B, -100)
            time.sleep(0.5)
            BP.set_motor_power(BP.PORT_B, 0)
            BP.set_motor_power(BP.PORT_B, BP.MOTOR_FLOAT)
        holdMqtt = False
        # BP.set_motor_power(BP.PORT_B, BP.MOTOR_FLOAT)
        # BP.set_motor_power(BP.PORT_C, BP.MOTOR_FLOAT)

client.on_message = messageCallback
client.loop_start()

print("Logging motor value and ready to take nudging messages...")

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

    while True:
        timeStamp = datetime.now().strftime('%H:%M:%S.%f')
        
        value_wrist = float(-BP.get_motor_encoder(BP.PORT_B))
        value_wrist = str(value_wrist)
        value_elbow = (BP.get_motor_encoder(BP.PORT_A) + BP.get_motor_encoder(BP.PORT_C)) * -1 / 2
        value_elbow = str(value_elbow)
        if not holdMqtt:
            client.publish("motor_value_wrist", value_wrist + "," + timeStamp, qos=0)
            client.publish("motor_value_elbow", value_elbow + "," + timeStamp, qos=0)
        logging.info(value_wrist + "," + value_elbow + "," + timeStamp)

        # time.sleep(0.02)

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        client.loop_stop()
        logging.info("program stopped")
        BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
