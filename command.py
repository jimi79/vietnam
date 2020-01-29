from const import *

class Command():
	def __init__(self, duration):
		self.id = None
		self.when = None
		self.auto_repeat = False
		if duration != None:
			self.duration = duration / SPEED_FACTOR
		else:
			self.duration = None

class CommandQuery(Command): # we ask a question, that interrupts what is going on
	def __init__(self, duration):
		super().__init__(duration)

class CommandLook(CommandQuery):
	def __init__(self):
		super().__init__(duration = 10)

class CommandStatus(CommandQuery):
	def __init__(self):
		super().__init__(duration = 5)

class CommandAction(Command):
	def __init__(self, duration):
		super().__init__(duration)

class CommandMove(CommandAction):
	def __init__(self):
		super().__init__(60)
		self.direction = None
		self.auto_repeat = True

class CommandAskWork(CommandAction): # interrupt, even if we just asks
	def __init__(self):
		super().__init__(duration = 5)

class CommandDoWork(CommandAction):
	def __init__(self, goal):
		super().__init__(goal.duration)
		self.goal = goal

class CommandFight(CommandAction):
	def __init__(self):
		super().__init__(30)
		self.auto_repeat = True
		self.killed = 0

class CommandStop(Command):
	def __init__(self):
		super().__init__(10)
	
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
			obj = CommandAskWork() 
		obj.id = query[0]['code']
		return obj
	
