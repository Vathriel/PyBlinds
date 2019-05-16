# PyBlinds

## Description
A super simple blinds program with open/close and sunrise/sunset features. 
It's meant to be used in conjunction with a raspberry pi and 5v motor.

Is the program efficient? No.
Is it practical? Not my call.
Is it glitch free or secure? No, and no.

## Attribution
Sunrise/Sunset API:
https://sunrise-sunset.org/api

Requests Library:
https://2.python-requests.org//en/master/

## Setup
I used this with a stepper motor, and some of the code took inspiration or root from here:
https://medium.com/@Keithweaver_/controlling-stepper-motors-using-python-with-a-raspberry-pi-b3fbd482f886

You should use a similar setup with this program, the only library you should need to download on the pi would be Requests. 

## Running the blinds
The code itself is fairly straight forward, the motor can be ran in two directions, the starting position should be blinds neutral in my case. The motor will not run further in the same direction after the cycle has ended, position is saved to a file to prevent such. 

It's easiest to start one of these commands by either using a keyboard mouse and monitor with the raspberrypi or with a network connection and SSH.

`python blinds.py open`
Opens the blinds

`python blinds.py close`
Closes the blinds

`python blinds.py sun`
Recursively schedules sunrises/sunsets

## Future Plans
I do not plan on supporting this project further, it has met it's goals. 
