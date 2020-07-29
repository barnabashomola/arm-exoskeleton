#!/usr/bin/env python
from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division

import paho.mqtt.client as mqtt # import mqtt library. Get the library with 'pip install paho-mqtt'
import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers
from datetime import datetime
import logging # python logging library to make the local logs 
import os # in order to be able to set the time on the first mqtt message

print("Setting up MQTT...")

# The name of the mqtt client, so the others know the messages belong to the exoskeleton
client = mqtt.Client("raspi_controller") 
# The IP address of the mqtt broker. Change this when the IP of the broker changes.
client.connect("192.168.0.6")
# client.connect("172.20.10.2")
# client.connect("192.168.0.100")

# Creating the local log file
logging.basicConfig(filename='exoskeleton.log', filemode="w", format='%(message)s', level=logging.DEBUG)
logging.info("value_wrist,value_elbow,timestamp") # log header

# Testing the mqtt connection by sending a test message
client.publish("test", "initial_test_message")
print("Initial MQTT test message sent")

# Subscribing to mqtt topics "nudge" for taking the motor commands and "time" for setting the time based on the Unity program's time to synchronize logs
print("Subscribing to nudging topic..")
#client.subscribe("motor_command_wrist")
#client.subscribe("motor_command_elbow")
client.subscribe("nudge", qos=1)
client.subscribe("time", qos=1)

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

holdMqtt = False # By changing this flag we are not sending mqtt messages. This is used during the time when the nudge movement is happening

# The mqtt callback which is called upon every message received
def messageCallback(client, userdata, message):
    print("Getting message on topic: " + str(message.topic))

    if str(message.topic)== "time":
        # Setting the date(time) of the raspberry pi based on the message payload coming from the Unity program (or other system)
        date_str = str(message.payload.decode("utf-8"))
        os.system('sudo date -s %s' % date_str)

    # if str(message.topic)== "motor_command_wrist":
    #     message = str(message.payload.decode("utf-8"))
    #     BP.set_motor_power(BP.PORT_C, int(message))

    # if str(message.topic)== "motor_command_elbow":
    #     message = str(message.payload.decode("utf-8"))
    #     BP.set_motor_power(BP.PORT_B, int(message))

    if str(message.topic)== "nudge":
        holdMqtt = True # Disabling mqtt communication

        message = str(message.payload.decode("utf-8"))
        print(message)
        if message == "up":
            target = BP.get_motor_encoder(BP.PORT_C) - 100
            BP.set_motor_position(BP.PORT_C + BP.PORT_A, target)
            # BP.set_motor_power(BP.PORT_C + BP.PORT_A, 100)
            time.sleep(0.5) # wait until the movement is done
            BP.set_motor_power(BP.PORT_C + BP.PORT_A, BP.MOTOR_FLOAT) # releasing the motor to make it able to be moved again
        elif message == "down":
            target = BP.get_motor_encoder(BP.PORT_C) + 100
            BP.set_motor_position(BP.PORT_C + BP.PORT_A, target)
            # BP.set_motor_power(BP.PORT_C + BP.PORT_A, -100)
            time.sleep(0.5) # wait until the movement is done
            BP.set_motor_power(BP.PORT_C + BP.PORT_A, BP.MOTOR_FLOAT) # releasing the motor to make it able to be moved again
        elif message == "left":
            target = BP.get_motor_encoder(BP.PORT_B) + 100
            BP.set_motor_position(BP.PORT_B, target)
            # BP.set_motor_power(BP.PORT_B, 100)
            time.sleep(0.5) # wait until the movement is done
            BP.set_motor_power(BP.PORT_B, BP.MOTOR_FLOAT) # releasing the motor to make it able to be moved again
        elif message == "right":
            target = BP.get_motor_encoder(BP.PORT_B) - 100
            BP.set_motor_position(BP.PORT_B, target)
            # BP.set_motor_power(BP.PORT_B, -100)
            time.sleep(0.5) # wait until the movement is done
            BP.set_motor_power(BP.PORT_B, BP.MOTOR_FLOAT) # releasing the motor to make it able to be moved again
            
        holdMqtt = False # Enabling mqtt communication again
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
            # Streaming the sensor values as mqtt messages
            client.publish("motor_value_wrist", value_wrist + "," + timeStamp, qos=0)
            client.publish("motor_value_elbow", value_elbow + "," + timeStamp, qos=0)
        # Creating local log entry
        logging.info(value_wrist + "," + value_elbow + "," + timeStamp)

        
        # time.sleep(0.02) # Sleep in every cycle. By increasing it, the CPU of the Pi is less stressed and the mqtt messages are more stable but the sensor values are less frequent and accurate

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
        client.loop_stop()
        logging.info("program stopped")
        BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
