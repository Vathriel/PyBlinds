# PyBlinds

## Description
A super simple blinds program with open/close and sunrise/sunset features. 
It's meant to be used in conjunction with a raspberry pi and 5v motor.

Is the program efficient? No.
Is it practical? Not my call.
Is it glitch free or secure? No, and no.

## Attribution
The sunrise/sunset feature does not use a light sensor, rather it pulls from a web api.
Specifically: https://sunrise-sunset.org/api


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
