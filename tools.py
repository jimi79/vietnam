import datetime
import random
from const import *
import math

def rnd():
	return random.randrange(0, SIZE) 

def debug(text):
	if DEBUG:
		f = open("debug", "a")
		f.write("%s: %s\n" % (datetime.datetime.now().strftime("%H:%M:%S"), text)) 

def roundDistance(value):
	approxs = [1,2,5,8,10,15,20,30,40,50,60,70,100,150,200,300,400,500]
	dists = [(a, abs(a - value)) for a in approxs]
	dists.sort(key = lambda x:abs(x[1]))
	return dists[0][0]

def vagueDistance(value):
	if value > 50:
		res = "very far away"
	else:
		if value > 20:
			res = "far away"
		else:
			res = "not too far away"
#	res = "%s %0.2f" % (res, value)
	return res

def getDirection(fromY, fromX, toY, toX):
	angle = math.degrees(math.atan2(toY - fromY, toX - fromX))
	sd = ["east", "south east", "south", "south west", "west", "north west", "north", "north east"] 
	return angle, sd[round(angle / 45) % 8]

def getDistance(fromY, fromX, toY, toX):
	return math.sqrt(math.pow(abs(fromY - toY), 2) + math.pow(abs(fromX - toX), 2))



