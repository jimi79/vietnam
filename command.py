import random
from tools import *
from const import *

class Command():
	def __init__(self):
		self.id = None
		self.when = None
		self.auto_repeat = False
		self.factor_duration = 1 #used when moving in diag, could be used if less than x ppl when u work

	def get_duration(self):
		d = self.duration[0]
		if self.duration[1] != None:
			d = d + self.rand(self.duration[1])
		d = d / SPEED_FACTOR
		d = d * self.factor_duration
		log("new duration = %0.0f" % d)
		return d

	def rand(self, delta):
		return (random.randrange(1, 11)) * (random.randrange(0, 2) * 2 - 1)

class CommandInsert(Command): # we ask a question, that interrupts what is going on
	def __init__(self):
		super().__init__()

class CommandLook(CommandInsert):
	def __init__(self):
		self.duration = (10, 2)
		super().__init__()

class CommandStatus(CommandInsert):
	def __init__(self):
		self.duration = (5, None)
		super().__init__()

class CommandQueued(Command):
# queued mean we queue after other non queued command, but we erase queued commands
	def __init__(self):
		super().__init__()

class CommandMove(CommandQueued):
	def __init__(self):
		self.duration = (60, None)
		super().__init__()
		self.direction = None
		self.auto_repeat = True

class CommandAskWork(CommandQueued): # interrupt, even if we just asks
	def __init__(self):
		self.duration = (5, None)
		super().__init__()

class CommandDoWork(CommandQueued):
	def __init__(self, goal):
		self.duration = (goal.duration, 10)
		super().__init__()
		self.goal = goal

class CommandFight(CommandInsert): # not an action
	def __init__(self):
		self.duration = (30, None)
		super().__init__()
		self.auto_repeat = True
		self.killed = 0

class CommandStop(Command):
	def __init__(self):
		self.duration = (10, None)
		super().__init__()

class CommandPatrol(CommandQueued):
	def __init__(self, locations, y, x):
		self.duration = (180, 120)
		super().__init__()
		self.locations = locations
		self.x = x
		self.y = y
		self.auto_repeat = True
	
class ParseQueryToCommand():
	def parse(self, query):
		query = query.query # to get the actual json thing
		if query[1]['code'] == COMMAND_LOOK:
			obj = CommandLook()
		if query[1]['code'] == COMMAND_STATUS:
			obj = CommandStatus()
		if query[1]['code'] == COMMAND_STOP:
			obj = CommandStop()
		if query[1]['code'] == COMMAND_MOVE:
			obj = CommandMove()
			obj.direction = query[2]['code']
			if len(obj.direction) > 1: #trick: ne is diag, n is straight
				obj.factor_duration = 1.4 # sqr 2
		if query[1]['code'] == COMMAND_WORK:
			obj = CommandAskWork() 
		obj.id = query[0]['code']
		return obj
	
