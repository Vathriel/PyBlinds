import RPi.GPIO as GPIO
import time
import sys
import requests
import json
import re
import datetime
#from datetime import datetime
from threading import Timer
#import urllib.request

moveSteps = 4096
lookUpInterval = 1 #idk what this should be, about a minute anyways.
PositionLog = 'Logs/LastPos.txt'

apistr = "https://api.sunrise-sunset.org/json?lat=40.541104&lng=-105.0356537&date=today"
apitomorrow = "https://api.sunrise-sunset.org/json?lat=40.541104&lng=-105.0356537&date=tomorrow"
utcmod = -6
p = re.compile(r"(\d?\d):(\d?\d):(\d?\d)\s*([a-zA-Z][a-zA-Z])")

control_pins = [7,11,13,15]
motorforward = [
	[0,0,0,1],
	[0,0,1,1],
	[0,0,1,0],
	[0,1,1,0],
	[0,1,0,0],
	[1,1,0,0],
	[1,0,0,0],
	[1,0,0,1],
]

motorbackward = [
	[1,0,0,0],
	[1,1,0,0],
	[0,1,0,0],
	[0,1,1,0],
	[0,0,1,0],
	[0,0,1,1],
	[0,0,0,1],
	[1,0,0,1],
]

def setup():
	GPIO.setmode(GPIO.BOARD)
	for pin in control_pins:
		GPIO.setup(pin, GPIO.OUT)
		GPIO.output(pin, 0)

def getPos(): #pulls the last position from the file
	#start pos = 0, open pos = moveSteps, close pos = -moveSteps
	posf = open(PositionLog,'r')
	outpos = 0
	try:
		l = posf.readline()
		outpos = int(l)
		print("Got current position: "+str(outpos))
		#Note, this may include a new line, if it does further work will be needed to
		#avoid issues with the int conversion.
	finally:
		posf.close()
	return outpos

def setPos(pos):
	posf = open(PositionLog,'w')
	try:
		posf.write(str(pos)) #need to make sure this overwrites the file properly.
		print("Set new position: "+str(pos))
	finally:
		posf.close()
	return 0

def cleanUp():
	print("------Cleaning------")
	GPIO.cleanup()


def RunOpen():
	print("------Opening------")

	cpos = getPos()
	if (cpos >= 0):
		print("Blinds are open already!")
	else:
		cpos = abs(cpos)

	setup()
	for i in range(cpos):
		for halfstep in range(8):
			for pin in range(4):
				GPIO.output(control_pins[pin], motorforward[halfstep][pin])
			time.sleep(0.001)
	setPos(0)
	return 1

def RunClose():
	print("------Closing------")
	cpos = getPos()
	if (cpos < 0):
		print("Blinds are closed already!")
	elif (cpos > 0):
		cpos = moveSteps + cpos
	else:
		cpos = moveSteps

	setup()
	for i in range(cpos):
		for halfstep in range(8):
			for pin in range(4):
				GPIO.output(control_pins[pin], motorbackward[halfstep][pin])
			time.sleep(0.001)
	setPos(-moveSteps)
	return 1


#start scheduling code
def CheckTime(t1,t2): #t1,t2 are passed as [hour, minute, second]
#If t1 > t2 return true else return false
	if (t1[0] > t2[0]):
		return True #yes t1 is in the future
	elif (t1[0] == t2[0]):
		if (t1[1] > t2[1]):
			return True #yes t1 is in the future
		elif(t1[1] == t2[1]):
			print("Not enough information to determine if t1 is in the future.")
			return -1
	return False

def getNow():
	dt = datetime.datetime.now()
	hour = dt.hour
	minute = dt.minute
	sec = dt.second
	return [hour,minute]

def getSunrise(d): #true for tomorrow.
	if d:
		resp = requests.get(url=apitomorrow)
		data = resp.json()["results"]
		Sunrise = data["sunrise"]
		SR = p.match(Sunrise)
		SR3 = str(SR.group(1)) + ":" + str(SR.group(2)) + " " + str(SR.group(4))
		t = datetime.datetime.strptime(SR3, '%I:%M %p')
		thour = t.hour + utcmod
		tmin = t.minute
		tsec = t.second
		return [thour,tmin]
	else:
		resp = requests.get(url=apistr)
		data = resp.json()["results"]
		Sunrise = data["sunrise"]
		SR = p.match(Sunrise)
		SR3 = str(SR.group(1)) + ":" + str(SR.group(2)) + " " + str(SR.group(4))
		t = datetime.datetime.strptime(SR3, '%I:%M %p')
		thour = t.hour + utcmod
		tmin = t.minute
		tsec = t.second
		return [thour,tmin]

def getSunset():
	resp = requests.get(url=apistr)
	data = resp.json()["results"]
	Sunset = data["sunset"]
	SS = p.match(Sunset)
	SR3 = str(SS.group(1)) + ":" + str(SS.group(2)) + " " + str(SS.group(4))
	t = datetime.datetime.strptime(SR3, '%I:%M %p')
	thour = t.hour +utcmod
	tmin = t.minute
	tsec = t.second
	if thour < 0:
		x = datetime.datetime.today()
		x = x.replace(day=x.day,hour=(24+thour),minute=tmin,second=0,microsecond=0)
		thour = x.hour
		tmin = x.minute
	return [thour,tmin]

def Schedule(tic):
	if (tic == 0): #scheduling for sunrise
		#check current time against this, run, call Schedule(1) if fail
		sr = getSunrise(False) #get today sunrise
		n = getNow() #get current time
		if CheckTime(sr,n):
			print("------Sunrise Scheduled------")
			x = datetime.datetime.today()
			y = x.replace(day=x.day, hour=sr[0], minute=sr[1], second=0, microsecond=0)
			delta = y-x
			s = delta.seconds+1
			t = Timer(s,RunOpen)
			t.start()
			time.sleep(s)
			Schedule(1)#schedule for the sunset
		else:
			print("------Failed Sunrise Schedule------")
			Schedule(1)
	elif(tic == 1): #scheduling for sunset
		#check current time against this, run, call Schedule(2) if fail
		ss = getSunset()
		n = getNow()
		if CheckTime(ss,n):
			print("------Sunset Scheduled------")
			x = datetime.datetime.today()
			y = x.replace(day=x.day, hour=ss[0], minute=ss[1], second=0, microsecond=0)
			delta = y-x
			s = delta.seconds+1
			t = Timer(s,RunClose)
			t.start()
			time.sleep(s)
			Schedule(2) #schedule for the next sunrise
		else:
			print("------Failed Sunset Schedule------")
			Schedule(2)
	elif(tic == 2): #scheduling for tomorrow sunrise
		print("------Sunrise Scheduled------")
		sr = getSunrise(True)
		#t = getNow()
		x = datetime.datetime.today()
		y = x.replace(day=x.day, hour=sr[0], minute=sr[0], second=0, microsecond=0) + datetime.timedelta(days=1)
		delta = y-x
		s = delta.seconds+1
		t = Timer(s,RunOpen)
		t.start()
		time.sleep(s)
		Schedule(1) #schedule next sunset

def main(argv):
	print("------Starting------")
	if (argv[0] == "close"):
		if (RunClose() > 0): #no need to clean up if we fail.
			cleanUp()
	elif (argv[0] == "open"):
		if (RunOpen() > 0):
			cleanUp()
	elif (argv[0] == "sun"):
		print("------Checking Schedule------")
		Schedule(0)
	else:
		print("Usage:\npython blinds.py {arg}\nArg: open, close, sun\nEx: python blinds.py open")


if __name__ == "__main__":
	main(sys.argv[1:])
