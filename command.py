import random
import datetime
import json
from tools import *
from const import *

class Command():
	def __init__(self):
		self.id = None
		self.when = None
		self.autoRepeat = False
		self.factorDuration = 1 #used when moving in diag, could be used if less than x ppl when u work
		self.priority = None
		self.removeLower = False # if accepted, remove anythg under it
# like moving will remove all tasks with similar priority (moving and working)
		self.blocking = False # if True, then won't accept any lower priority tasks
		self.removeSimilar = True # default behavior, we remove similar requests
		self.canBeRemoved = True # false if cannot be removed, like patrolling for a NPC
		self.removeGroup = []
		self.group = None

	def getDuration(self):
		d = self.duration[0]
		if self.duration[1] != None:
			d = d + self.rand(self.duration[1])
		d = d / SPEED_FACTOR
		d = d * self.factorDuration
		self.calculatedDuration = d
		return d

	def rand(self, delta):
		c = (random.randrange(1, 1 + delta)) * (random.randrange(0, 2) * 2 - 1)
		c = max(1, c)
		return c

class CommandLook(Command):
	def __init__(self):
		self.duration = (5, 2)
		super().__init__()
		self.priority = 3

class CommandDoGetDirections(Command):
	def __init__(self):
		self.duration = (120, 40)
		super().__init__()
		self.priority = 3

class CommandGoingBackToBase(Command):
	def __init__(self):
		self.duration = (120, 40)
		super().__init__()
		self.priority = 3

class CommandStatus(Command):
	def __init__(self):
		self.duration = (2, 1)
		super().__init__()
		self.priority = 3

class CommandMove(Command):
	def __init__(self):
		self.duration = (60, 10)
		super().__init__()
		self.direction = None
		self.autoRepeat = True
		self.priority = 1
		self.removeGroup = 'M'
		self.group = 'M'

class CommandMoveOnce(Command):
	def __init__(self):
		self.duration = (60, 10)
		super().__init__()
		self.direction = None
		self.autoRepeat = False
		self.priority = 1
		self.removeGroup = 'M'
		self.group = 'M'

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
	def __init__(self, countBefore):
		self.duration = (5, 1)
		super().__init__()
		self.autoRepeat = True
		self.killed = 0
		self.priority = 5
		self.removeLower = True
		self.blocking = True
		self.countBefore = countBefore

class CommandStop(Command):
	def __init__(self):
		self.duration = (2, 1)
		super().__init__()
		self.priority = 4 # not 5, because a fight can't be stopped

class CommandPatrol(Command):
	def __init__(self, locations, y, x):
		self.duration = (180, 120)
		super().__init__()
		self.locations = locations
		self.x = x
		self.y = y
		self.autoRepeat = True
		self.priority = 3
		self.canBeRemoved = False

class CommandAskGetDirections(Command):
	def __init__(self):
		self.duration = (5, 2)
		super().__init__()
		self.priority = 4

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
				obj.factorDuration = 1.4 # sqr 2
		if query[1]['code'] == COMMAND_WORK:
			obj = CommandAskWork()
		obj.id = query[0]['code']
		return obj

class Commands():
	def __init__(self):
		self.list = []

	def removeCommand(self, i):
		removed = self.list[i]
		for c in self.list[i:]:
			c.when = c.when - datetime.timedelta(seconds = removed.calculatedDuration) # when we inserted the task, we added that delay, so we simply remove it
		removed = self.list.pop(i)

	def insertCommand(self, i, command):
		for c in self.list[i:]:
			c.when = c.when + datetime.timedelta(seconds = command.calculatedDuration) # when we inserted the task, we added that delay, so we simply remove it
		self.list.insert(i, command)

	def calculateWhen(self, command, commandIndex):
		if commandIndex == 0:
			previousCommandTime = datetime.datetime.now()
		else:
			previousCommandTime = self.list[commandIndex - 1].when
		command.when = previousCommandTime + datetime.timedelta(seconds = command.getDuration())

	def add(self, command):
#TODO handle blocking
		l = [0] + [command.priority for command in self.list if command.blocking]
		highestCurrentPriority = max(l)
		if command.priority <= highestCurrentPriority:
			return False

		if command.removeSimilar:
			for i in range(len(self.list) - 1, -1, -1):
				if isinstance(command, self.list[i].__class__):
					self.removeCommand(i)

		for group in  command.removeGroup:
			for i in range(len(self.list) - 1, -1, -1):
				if command.group == group:
					self.removeCommand(i)

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

		if command.removeLower:
			i = 0
			while i < len(self.list):
				c = self.list[i]
				if c.priority > command.priority:
					i = i + 1
					if i >= len(self.list):
						break
				else:
					if self.list[i].canBeRemoved:
						self.removeCommand(i)
					else:
						i = i + 1
		self.calculateWhen(command, rank)
		self.insertCommand(rank, command)
		return True

	def debug(self):
		a = []
		for command in self.list:
			a.append("type:%s, duration: %0.0f, when: %s" % (str(command), command.calculatedDuration, command.when.strftime("%H:%M:%S")))
		return "\n".join(a)

	def getDebugLetters(self):
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
