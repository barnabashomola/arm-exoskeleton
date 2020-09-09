# arm-exoskeleton
This repository holds the code, logs and other relevant materials for the LEGO arm-exoskeleton designed and developed by students at the Technical University of Denmark.

# Tutorial

## Setup

### Lego setup
In order to set up the arm exokeleton you need to assemble the Lego hardware. The [manual](https://github.com/barnabashomola/arm-exoskeleton/blob/master/lego_model/LEGO%20Arm%20Exoskeleton%20Mk%201manual.pdf) can be found in the repo as a pdf document. 

For additional information and the specific needed brick list please open the [model folder](https://github.com/barnabashomola/arm-exoskeleton/tree/master/lego_model). Here you can find 3D models of the exoskeleton which can be opened with the [BrickLink Studio](https://www.bricklink.com/v3/studio/download.page) program.

Furthermore there is an [XML file with the needed parts](https://github.com/barnabashomola/arm-exoskeleton/blob/master/lego_model/LEGO%20Arm%20Exoskeleton%20Mk1.xml). This XML contains **ALL** the needed LEGO parts (including EV3 Large Servo motors and the Mindstorms cables). This XML file can be imported into one of the known LEGO brick database websites ([Bricklink](https://www.bricklink.com/) or [BrickOwl](https://www.brickowl.com/)) as wanted set-list and therefore can be ordered.

### Raspberry Pi setup
The exoskeleton is powered by a Raspberry Pi extended by a [BrickPi](https://www.dexterindustries.com/brickpi/) extension board which provides the interface to the Lego EV3 sensors. Follow the instructions on BrickPi's website to assemble the acryllic case. The case can be attached to the right side of the model at the upper-arm part. (NB: This orientation can be changed by restructuring the exoskeleton a little bit)

For the software setup, also follow the corresponding [BrickPi documentation](https://www.dexterindustries.com/BrickPi/brickpi-tutorials-documentation/getting-started/pi-prep/).

In order to use the wireless communication feature of the exoskeleton, the Raspberry Pi needs to be connected to the same network as the MQTT broker. For connecting the Raspberry Pi to a wireless network please see [the official documentation](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md).

The sensors need to be connected in the given order to the BrickPi:
* The Large EV3 servo motor at the wrist: **Port B**
* The two Large EV3 servo motors at the elbow joint: **Port A and Port C**

The system is powered by 8 AA batteries which are sitting in the battery rack provided by the BrickPi set. In order to mount it on the exoskeleton, apply velcro straps to the opposite side of the upper-arm part of the exoskeleton to where the BrickPi is placed, then apply velcro on the battery rack as well and "stick it" to the exoskeleton. (See pictures)

<img src="https://github.com/barnabashomola/arm-exoskeleton/blob/master/pictures/control_unit_placement.jpg" alt="Control unit placement" width="400"/>
<img src="https://github.com/barnabashomola/arm-exoskeleton/blob/master/pictures/exoskeleton.jpg" alt="Exoskeleton" width="400"/>

### Exoskeleton hardware setup
The recommended way of putting the exoskeleton on the arm is the following:
1. Open the wrist lock the widest position and lock it. (To unlock the wrist lock move the black gears to the center of the circle. To lock it, move the black gears back to the linear gear, that way locking it in. See pictures)
2. Bend the exoskeleton at the elbow joint so the upper-arm part is bended over the wrist part.
3. Slowly move the hand through the wrist cuff.
4. Unlock the wrist cuff, tighten it gently, but well to the user's wrist. The cuff should be located a bit above the wrist bones.
5. Bend the upper-arm part on the user's arm. Make sure that the elbow joint gears are sitting right at the elbow and are aligned.
6. Use the velcro straps to tighten the structure to the arm.

<img src="https://github.com/barnabashomola/arm-exoskeleton/blob/master/pictures/velcro.png" alt="Velcro" width="400"/>
<img src="https://github.com/barnabashomola/arm-exoskeleton/blob/master/pictures/locking_mechanism.jpg" alt="Locking mechanism" width="400"/>


### MQTT Setup
The exoskeleton uses the [MQTT protocol](http://mqtt.org/) to communicate with other systems. In order to use the exoskeleton you have to set up an MQTT broker (server) to which the exoskeleton and the other systems (e.g. Unity program) will connect.

Many options are available to set up your own local MQTT broker. One of the most popular one is the [Mosquitto](https://mosquitto.org/) open source broker.

## Usage

1. Boot up the Raspberry Pi
2. SSH into the Pi (https://www.raspberrypi.org/documentation/remote-access/ssh/) (By default it's: ```ssh pi@dex.local```)
3. Place the [exoskeleton python script](https://github.com/barnabashomola/arm-exoskeleton/blob/master/exoskeleton.py) to directory
4. Open the ```exoskeleton.py``` script with your favourite text editor (VIM, nano...)
5. Modify the IP address in line 14 to the IP address of the MQTT broker as the following: ```client.connect("<IP_ADDRESS_OF_MQTT_SERVER>")```. If you are running a local MQTT broker on your own computer then it will be your own IP. Save and close the file.
6. Make sure that your MQTT broker is running.
7. Start the program by typing ```python exoskeleton.py```.
8. The program will give you messages and once you've seen all these messages appear the program is up and running, connected to the MQTT broker.
```
Setting up MQTT...
Initial MQTT test message sent
Subscribing to nudging topic..
Logging motor value and ready to take nudging messages...
```

### Sending nudging messages
In order to send nudging messages (for example from a Unity game) send a right MQTT message to the broker.
* Message topic: ```nudge```
* Message payload: ```up``` or ```down``` or ```left``` or ```right```

On receiving any of these messages, the exoskeleton will move to the given direction, providing a small nudge to the wearer. Up and down will move the elbow joint while left or right will move the wrist joint.

## Data logging
While the program is running it creates a log in the directory where the ```exoskeleton.py``` is located. It is a comma separated values (CSV) file with the following format: The first line describes the columns: value_wrist, value_elbow and timestamp. This header is followed by the values which are logged as frequent as the Raspberry Pi program runs a cycle. It can be controlled by changing the ```time.sleep(<YOUR_VALUE>)``` line in the main cycle. 

The log file is deleted on every run, so make sure to save it if you want to use it later.
