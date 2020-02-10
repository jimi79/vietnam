import datetime
import random
from const import *

def rnd():
	return random.randrange(0, SIZE) 

def log(text):
	if DEBUG:
		f = open("debug", "a")
		f.write("%s: %s\n" % (datetime.datetime.now().strftime("%H:%M:%S"), text)) 
