# arm-exoskeleton
This repository holds the code, logs and other relevant materials for the LEGO arm-exoskeleton designed and developed by students at the Technical University of Denmark.

## Coming soon
* Step-by-step tutorial on setting up the exoskeleton is coming soon


# Tutorial

## Setup

### Lego setup
In order to set up the arm exokeleton you need to assemble the Lego hardware. The manual can be found as part of the [report](https://github.com/barnabashomola/arm-exoskeleton/blob/master/documents/Exoskeleton___Final_report.pdf). For additional information and the specific needed brick list please open the [model folder](https://github.com/barnabashomola/arm-exoskeleton/tree/master/lego_model). Here you can find 3D models of the exoskeleton which can be opened with the [BrickLink Studio](https://www.bricklink.com/v3/studio/download.page) program.

### Raspberry Pi setup
The exoskeleton is powered by a Raspberry Pi extended by a [BrickPi](https://www.dexterindustries.com/brickpi/) extension board which provides the interface to the Lego EV3 sensors. Follow the instructions on BrickPi's website to assemble the acryllic case. The case can be attached to the right side of the model at the upper-arm part. (NB: This orientation can be changed by restructuring the exoskeleton a little bit)

For the software setup, also follow the corresponding [BrickPi documentation](https://www.dexterindustries.com/BrickPi/brickpi-tutorials-documentation/getting-started/pi-prep/)

The sensors need to be connected in the given order to the BrickPi:
* The Large EV3 servo motor at the wrist: **Port B**
* The two Large EV3 servo motors at the elbow joint: **Port A and Port C**

The system is powered by 8 AA batteries which are sitting in the battery rack provided by the BrickPi set. In order to mount it on the exoskeleton, apply velcro straps to the opposite side of the upper-arm part of the exoskeleton to where the BrickPi is placed, then apply velcro on the battery rack as well and "stick it" to the exoskeleton. (See pictures)

## Usage

## Data logging
