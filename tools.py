import datetime
import random
from const import *

def rnd():
	return random.randrange(0, SIZE) 

def log(text):
	f = open("log", "a")
	f.write("%s: %s\n" % (datetime.datetime.now().strftime("%H:%M:%S"), text)) 
