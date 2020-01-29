from const import *

class Command():
	def __init__(self):
		self.id = None
		self.when = None
		self.auto_repeat = False
		self.duration = None

class CommandQuery(Command): # we ask a question, that interrupts what is going on
	def __init__(self):
		super().__init__()

class CommandLook(CommandQuery):
	def __init__(self):
		super().__init__()
		self.duration = 10 / SPEED_FACTOR

class CommandStatus(CommandQuery):
	def __init__(self):
		super().__init__()
		self.duration = 5 / SPEED_FACTOR 

class CommandAction(Command):
	def __init__(self):
		super().__init__()

class CommandMove(CommandAction):
	def __init__(self):
		super().__init__()
		self.direction = None
		self.duration = 60 / SPEED_FACTOR # if in an angle, do that times sqr(2)...
		self.auto_repeat = True

class CommandWork(CommandAction):
	def __init__(self):
		super().__init__()
		self.duration = None # determined by the map, no idea how i will do that. 
# i think team knows map, and so can say the duration of a given work
# but a 'work' object should be better
# we'll see....

class CommandFight(CommandAction):
	def __init__(self):
		super().__init__()
		self.duration = 30 / SPEED_FACTOR
		self.auto_repeat = True
		self.killed = 0

class CommandStop(Command):
	def __init__(self):
		super().__init__()
		self.duration = 10 / SPEED_FACTOR
	

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
				obj.duration = obj.duration * 1.4 # sqr 2
		if query[1]['code'] == COMMAND_WORK:
			obj = CommandWork() 
		obj.id = query[0]['code']
		return obj
	
