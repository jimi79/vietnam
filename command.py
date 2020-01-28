from const import *

class Command():
	def __init__(self):
		self.id = None
		self.when = None

class CommandLook(Command):
	def __init__(self):
		self.duration = 10 / SPEED_FACTOR

class CommandAction(Command):
	pass

class CommandMove(CommandAction):
	def __init__(self):
		self.direction = None
		self.duration = 60 / SPEED_FACTOR # if in an angle, do that times sqr(2)...

class CommandWork(CommandAction):
	def __init__(self):
		self.duration = None # determined by the map, no idea how i will do that. 
# i think team knows map, and so can say the duration of a given work
# but a 'work' object should be better
# we'll see....

class ParseQueryToCommand():
	def parse(self, query):
		query = query.query # to get the actual json thing
		if query[1]['code'] == COMMAND_LOOK:
			obj = CommandLook()
		if query[1]['code'] == COMMAND_MOVE:
			obj = CommandMove()
			obj.direction = query[2]['code']
			if len(obj.direction) > 1:
				obj.duration = obj.duration * 1.4 # sqr 2
		if query[1]['code'] == COMMAND_WORK:
			obj = CommandWork() 
		obj.id = query[0]['code']
		return obj
