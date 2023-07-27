import datetime
import copy
import math
from tools import *
from command import *
from reply import *
from goal import *
from writelog import *

class Team():
	def __init__(self, id_, name): 
		self.id = id_
		self.commands = Commands()
		self.nato = name
		self.letter = name[0] 
		self.replies = [] # list of messages returned by the team 
		self.otherTeams = None 
		self.ourTeams = None 
		self.npc = False
		self.fighting = False

	def getDirection(self, desty, destx):
		y = self.y
		x = self.x
		return getDirection(desty, destx, y, x) # we want the team compare to the destination

	def getDistance(self, desty, destx):
		y = self.y
		x = self.x
		return getDistance(y, x, desty, destx)

	def addReply(self, value):
		if not self.npc:
			reply = Reply(value, self)
			self.replies.append(reply)
	
	def dumpReplies(self):
		if self.getAlive():
			r = copy.copy(self.replies)
		else: 
			r = []
		self.replies = []
		return r
	
class TeamInfantry(Team):
	def __init__(self, id_, count, goals, y, x, name): 
		super().__init__(id_, name = name)
		self.goals = goals
		self.y = y
		self.x = x
		self.exited = False
		self.count = count 
	
	def tick(self): 
# we don't handle fight here, fights are handled by somethg else.
# but still, there is a command added to the list, that will prevent other commands to be added
		if not self.getExists():
			self.commands.reset()
			return

		if len(self.commands.list) > 0:
			command = self.commands.list[0] 
			if command.when <= datetime.datetime.now():
				self.commands.list.pop(0) 
# no need to rewrite the command, bc it pops up as long as there are ennemies anyway
				if isinstance(command, CommandFight):
					pass
				elif isinstance(command, CommandStop):
					self.commands.reset()
					self.addReply('we stopped') 
				elif isinstance(command, CommandLook):
					self.doLook()
				elif isinstance(command, CommandStatus): 
					self.addReply(self.status())
				elif isinstance(command, CommandMove) or isinstance(command, CommandMoveOnce):
					if not self.doMove(command):
						command.autoRepeat = False
				elif isinstance(command, CommandPatrol):
					self.doPatrol(command)
				elif isinstance(command, CommandAskWork):
					self.doAskWork()
				elif isinstance(command, CommandDoWork):
					self.doWork(command)
				else:
					raise Exception("instance of %s not handled" % str(command))
				if command.autoRepeat:
					self.commands.add(command)

	def getAlive(self):
		return (self.count > 0)
	
	def getExists(self):
		return (not self.exited) and (self.count > 0)

	def getPosFromDirection(self, direction):
		y = self.y + (1 if "s" in direction else -1 if "n" in direction else 0)	
		x = self.x + (1 if "e" in direction else -1 if "w" in direction else 0)	
		return y, x 

	def lookForWonders(self, y, x):
		res = [] # list of strings
		for wonder in self.map.placedWonders:
			destY = wonder.y
			destX = wonder.x
			distance = getDistance(y, x, destY, destX)
			if distance >= 2: # if less than 2, then it's around, so it's in the first round description
				direction = getDirection(y, x, destY, destX)[1]
				if distance * CELL_RESOLUTION <= wonder.wonder.maxDistanceVisibility:
					res.append("We can see the %s in the %s, %s" % (wonder.wonder.name, direction, vagueDistance(distance * CELL_RESOLUTION)))

		return res

	def getItemAtPos(self, direction):
		items = []
		if direction != "l":
			y, x = self.getPosFromDirection(direction)
			sDirection = direction.upper()
		else:
			y = self.y
			x = self.x
			sDirection = "here"
		if x < 0 or y < 0 or x >= SIZE or y >= SIZE:
			items.append("a border")
		else: 
			if self.map.geo[y][x] == FOREST:
				items.append("a forest")
			if self.map.wonder[y][x] != None:
				items.append(self.map.wonder[y][x])
			else:
				if self.map.geo[y][x] == WATER:
					items.append("some water")  # if there is a wonder, no need to mention the water, it's obvious

			if self.map.geo[y][x] != FOREST: # can't see an ennemy in the forest
				if self.otherTeams != None:
					c = 0
					c = sum([a.count for a in self.otherTeams.getInfrantryList() if a.x == x and a.y == y])
					if c > 0:
						if c < 5:
							r = 5
						else:
							r = round(c / 5, 0) * 5
						items.append("around %d soldiers" % (r))
				for team in [a for a in self.ourTeams.getInfrantryList() if a.x == x and a.y == y and a.id != self.id and a.getExists()]:
					items.append("team %s" % team.nato)
			for goal in self.goals.list:
				if goal.x == x and goal.y == y:
					items.append("goal %s" % goal.name)
		
		if len(items) == 0:
			txt = None
		else:
			if len(items) > 1:
				s = "%s and %s" % (", ".join(items[0:-1]), items[-1])
			else:
				s = items[0]
			txt = "%s: %s" % (sDirection, s)
		return txt

	def getEnnemiesAtPos(self, direction = "l"): 
		y, x = self.getPosFromDirection(direction)
		teams = [team for team in self.otherTeams.getInfrantryList() if team.x == x and team.y == y and team.count > 0]
		return teams
	
	def look(self): 
		items = [] 
		for d in ["l", "n", "ne", "e", "se", "s", "sw", "w", "nw"]:
			item = self.getItemAtPos(d)
			if item != None:
				items.append(item) 
		if len(items) == 0:
			items.append("nothing around us")

		for i in self.lookForWonders(self.y, self.x):
			items.append(i)

		return 'we see: %s.' % ('. '.join(items))

	def doMove(self, command):
		direction = command.direction
		y = self.y + (1 if "s" in direction else -1 if "n" in direction else 0)	
		x = self.x + (1 if "e" in direction else -1 if "w" in direction else 0)	
		stop = False
		if y >= SIZE:
			self.addReply("we reached a border.")
			stop = True
		elif y < 0:
			self.addReply("we reached a border.")
			stop = True
		elif x >= SIZE:
			self.addReply("we reached a border.")
			stop = True
		elif x < 0:
			self.addReply("we reached a border.")
			stop = True
# if end up on water, then also refuse
		elif self.map.geo[y][x] == WATER:
			self.addReply("we can't go pass that water.")
			stop = True
		elif isinstance(command, CommandMoveOnce):
			self.addReply("we are at the new location.")
			self.commands.add(CommandLook())
		if stop:
			self.commands.add(CommandLook())
		else:
			self.y = y
			self.x = x
		return not stop

	def fighting(self):
		r = [c for c in self.commands.list if isinstance(c, CommandFight)]
		r = len(r) > 0
		return r

	def getGoalList(self):
		l = []
		for goal in self.goals.list:
			l.append(goal)
		s = []
		number = 1
		for goal in l:
			dist = round(self.getDistance(goal.y, goal.x))
			angle, sAngle = self.getDirection(goal.y, goal.x)
			s.append("goal %d: %s, direction: %s, distance: %0.0f hours." % (number, goal.name, sAngle, dist))
			number = number + 1
		return " ".join(s)

	def isHere(self, location):
		y, x = location
		return y == self.y and x == self.x 

	def status(self):
		s = ["we are %d people." % self.count]
		if len(self.commands.list) > 0: 
			if isinstance(self.commands.list[0], CommandLook):
				s.append('we are looking around.')

			elif isinstance(self.commands.list[0], CommandMove) or isinstance(self.commands.list[0], CommandMoveOnce):
				s.append('we are moving.')
			elif isinstance(self.commands.list[0], CommandDoWork):
				if isinstance(self.commands.list[0].goal, EndGoal):	
					s.append('we are evacuating.')
				else:
					s.append('we are working.')
		return ' '.join(s)

	def getNonEndGoalList(self):
		goals = [goal for goal in self.goals.list if not goal.done and not(isinstance(goal, EndGoal))]
		return goals

	def getGoalAtPos(self):
		goals = [goal for goal in self.goals.list if goal.x == self.x and goal.y == self.y]
		if len(goals) > 0:
			return goals[0]
		else:
			return None
	
	def doLook(self):
		self.addReply(self.look())

	def doWork(self, command):
		if isinstance(command.goal, EndGoal):
			self.exited = True
			self.addReply("we exited, bye")
		else:
			if command.goal.done:
				self.addReply("%s was done by someone else." % command.goal.name)
			else:
				command.goal.done = True 
				self.addReply("%s is done." % command.goal.name)

	def doPatrol(self, command):
		if self.x == command.x and self.y == command.y:
			random.shuffle(command.locations)
			self.y = command.locations[0][0]
			self.x = command.locations[0][1]
		else:
			self.x = command.x
			self.y = command.y

	def doAskWork(self):
		works = [g for g in self.goals.list if g.x == self.x and g.y == self.y]
		if len(works) == 0:
			self.addReply('there is nothing to do here.')
		else:
			work = works[0] # work at that pos
			doit = True
			if isinstance(work, EndGoal):
				works = [g for g in self.goals.list if (not isinstance(g, EndGoal)) and (not g.done)] # work left to be done
				if len(works) > 0:
					self.addReply("We can't evacuate right now, there are things to do.")
					doit = False
			else: 
				if work.done:
					self.addReply('this task is already done.')
					doit = False
			if doit:
				self.commands.add(CommandDoWork(work)) 

class TeamHelicopter(Team):
	def __init__(self, id_, name):
		super().__init__(id_ = id_, name = name)
		self.exited = False
	
	def tick(self): 
		if len(self.commands.list) > 0:
			command = self.commands.list[0]
			if command.when <= datetime.datetime.now():
				self.commands.list.pop(0)
				if isinstance(command, CommandAskGetDirections):
					if len(self.commands.list) == 0:
						self.addReply('we are taking off.')
						self.commands.add(CommandDoGetDirections())
					else:
						if (isinstance(self.commands.list[0], CommandDoGetDirections)):
							self.addReply("we are already on a reckon mission.")
						elif (isinstance(self.commands.list[0], CommandGoingBackToBase)):
							self.addReply("we can't doing reckon now, not enough fuel.")
						elif (isinstance(self.commands.list[0], CommandRefuelling)):
							self.addReply("we are busy refuelling.") 
						else:
							raise Exception("we have a %s" % str(self.commands.list[0]))
				elif isinstance(command, CommandDoGetDirections):
					self.doGetDirections()
				elif isinstance(command, CommandGoingBackToBase):
					self.goingBackToBase()
				elif isinstance(command, CommandRefuelling):
					self.addReply("refuelling done.") 
	
	def getAlive(self):
		return True
	
	def fighting(self):
		return False
	
	def doGetDirections(self):
		s = []
		l = [t for t in self.ourTeams.list if isinstance(t, TeamInfantry)]
		for team in l:
			if team.getExists():
				gl = team.goals.getPendingList()
				if len(gl) > 0:
					s2 = []
					for g in gl:
						dist = roundDistance(team.getDistance(g.y, g.x) * CELL_RESOLUTION)
						dir_ = team.getDirection(g.y, g.x)
						goalName = 'exit point' if isinstance(g, EndGoal) else 'the "%s" task' % g.name
						if dist < CELL_RESOLUTION:
							s2.append("close to %s" % (goalName))
						else:
							s2.append("at %0.0f km %s of %s" % (dist, dir_[1], goalName))
					s.append("team %s is %s." % (team.nato, ', '.join(s2)))
				else:
					s.append("team %s has nothing to do." % team.nato)
			else:
				s.append("team %s was not spotted." % team.nato)
		s.append("we're going back to the base.")
		#for a in s:
		self.addReply(" ".join(s))
		self.commands.add(CommandGoingBackToBase()) 

	def goingBackToBase(self): 
		self.addReply("we are back to the base, refuelling now.")
		self.commands.add(CommandRefuelling()) 

