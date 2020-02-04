import random
import datetime
import json
from tools import *
from const import *

class Command():
	def __init__(self):
		self.id = None
		self.when = None
		self.auto_repeat = False
		self.factor_duration = 1 #used when moving in diag, could be used if less than x ppl when u work
		self.priority = None
		self.remove_lower = False # if accepted, remove anythg under it
# like moving will remove all tasks with similar priority (moving and working)
		self.blocking = False # if True, then won't accept any lower priority tasks
		self.remove_similar = True # default behavior, we remove similar requests
		self.can_be_removed = True # false if cannot be removed, like patrolling for a NPC

	def get_duration(self):
		d = self.duration[0]
		if self.duration[1] != None:
			d = d + self.rand(self.duration[1])
		d = d / SPEED_FACTOR
		d = d * self.factor_duration
		self.calculated_duration = d 
		return d

	def rand(self, delta):
		return (random.randrange(1, 1 + delta)) * (random.randrange(0, 2) * 2 - 1)

class CommandLook(Command):
	def __init__(self):
		self.duration = (10, 2)
		super().__init__()
		self.priority = 3

class CommandGetDirection(Command):
	def __init__(self):
		self.duration = (10, 2)
		super().__init__()
		self.priority = 3

class CommandStatus(Command):
	def __init__(self):
		self.duration = (1, None)
		super().__init__()
		self.priority = 3

class CommandMove(Command):
	def __init__(self):
		self.duration = (60, None)
		super().__init__()
		self.direction = None
		self.auto_repeat = True
		self.priority = 1

class CommandMoveOnce(Command):
	def __init__(self):
		self.duration = (60, None)
		super().__init__()
		self.direction = None
		self.auto_repeat = False
		self.priority = 1

class CommandAskWork(Command):
	def __init__(self):
		self.duration = (5, 2)
		super().__init__()
		self.priority = 4 

class CommandDoWork(Command):
	def __init__(self, goal):
		self.duration = (goal.duration, 10)
		super().__init__()
		self.goal = goal
		self.priority = 1

class CommandFight(Command):
	def __init__(self):
		self.duration = (5, None)
		super().__init__()
		self.auto_repeat = True
		self.killed = 0
		self.priority = 5
		self.remove_lower = True
		self.blocking = True

class CommandStop(Command):
	def __init__(self):
		self.duration = (10, None)
		super().__init__()
		self.priority = 4 # not 5, because a fight can't be stopped

class CommandPatrol(Command):
	def __init__(self, locations, y, x):
		self.duration = (180, 120)
		super().__init__()
		self.locations = locations
		self.x = x
		self.y = y
		self.auto_repeat = True
		self.priority = 3
		self.can_be_removed = False

class CommandAskGetDirections(Command):
	def __init__(self):
		self.duration = (5, None)
		super().__init__()
		self.priority = 2
		
class CommandRefuelling(Command):
	def __init__(self):
		self.duration = (30, 10)
		super().__init__() 
		self.priority = 3
	
class ParseQueryToCommand():
	def parse(self, query):
		query = query.query # to get the actual json thing
		if query[1]['code'] == COMMAND_LOOK:
			obj = CommandLook() 
		if query[1]['code'] == COMMAND_GET_DIRECTIONS:
			obj = CommandAskGetDirections()
		if query[1]['code'] == COMMAND_STATUS:
			obj = CommandStatus()
		if query[1]['code'] == COMMAND_STOP:
			obj = CommandStop()
		if query[1]['code'] == COMMAND_MOVE or query[1]['code'] == COMMAND_MOVE_ONCE:
			if query[1]['code'] == COMMAND_MOVE:
				obj = CommandMove()
			else:
				obj = CommandMoveOnce()
			obj.direction = query[2]['code']
			if len(obj.direction) > 1: #trick: ne is diag, n is straight
				obj.factor_duration = 1.4 # sqr 2
		if query[1]['code'] == COMMAND_WORK:
			obj = CommandAskWork() 
		obj.id = query[0]['code']
		return obj
	
class Commands():
	def __init__(self):
		self.list = []
	
	def remove_command(self, i): 
		removed = self.list[i]
		for c in self.list[i:]:
			c.when = c.when - datetime.timedelta(seconds = removed.calculated_duration) # when we inserted the task, we added that delay, so we simply remove it 
		removed = self.list.pop(i)
	
	def insert_command(self, i, command): 
		for c in self.list[i:]:
			c.when = c.when + datetime.timedelta(seconds = command.calculated_duration) # when we inserted the task, we added that delay, so we simply remove it 
		self.list.insert(i, command)

	def calculate_when(self, command, command_index):
		if command_index == 0:
			previous_command_time = datetime.datetime.now()
		else:
			previous_command_time = self.list[command_index - 1].when
		command.when = previous_command_time + datetime.timedelta(seconds = command.get_duration())
	
	def add(self, command): 
#TODO handle blocking
		l = [0] + [command.priority for command in self.list if command.blocking] 
		highest_current_priority = max(l)
		if command.priority <= highest_current_priority:
			return False

		if command.remove_similar:
			for i in range(len(self.list) - 1, -1, -1):
				if isinstance(command, self.list[i].__class__):
					self.remove_command(i) 

		rank = None
		for i in range(0, len(self.list)):
			if command.priority >= self.list[i].priority:
				rank = i
				break
			else: # if the current comment has a higher rang
				if self.list[i].blocking:
					return False # then we exit everythg

		if rank == None:
			rank = len(self.list)
# we remove all inferior or equal priorities if the command says so
			
		if command.remove_lower:
			i = 0
			while i < len(self.list):
				c = self.list[i]
				if c.priority > command.priority:
					i = i + 1
					if i >= len(self.list):
						break
				else:
					if self.list[i].can_be_removed:
						self.remove_command(i)
					else:
						i = i + 1
		self.calculate_when(command, rank)
		self.insert_command(rank, command)
		return True

	def debug(self):
		a = []
		for command in self.list:
			a.append("type:%s, duration: %0.0f, when: %s" % (str(command), command.calculated_duration, command.when.strftime("%H:%M:%S")))
		return "\n".join(a)

	def get_debug_letters(self):
		a = ""
		for command in self.list:
			if isinstance(command, CommandLook):
				a = a + "L"
			if isinstance(command, CommandMove):
				a = a + "M"
			if isinstance(command, CommandFight):
				a = a + "F"
			if isinstance(command, CommandMoveOnce):
				a = a + "O"
			if isinstance(command, CommandStop):
				a = a + "S"
		return a

	def reset(self):
		self.list = []
