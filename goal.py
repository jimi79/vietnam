import random
from tools import *
from const import *

class Goal():
	def max_time(self):
		return 10 if DEBUG else 60 

	def __init__(self):
		self.x = rnd()
		self.y = rnd()
		self.duration = random.randrange(5, self.max_time()) # time in seconds
