import tools
import copy
from team import *

class Fight():
	def __init__(self, map_, teams1, teams2):
		self.map_ = map_
		self.teams1 = [t for t in copy.copy(teams1.list) if isinstance(t, TeamInfantry)]
		self.teams2 = [t for t in copy.copy(teams2.list) if isinstance(t, TeamInfantry)]
		for t in self.teams1:
			if t.fighting:
				t.stillFighting = False
		for t in self.teams2:
			if t.fighting:
				t.stillFighting = False

	def kill(self, teams, count):
		leftToKill = count
		debug("someone will kill %d" % count)
		for t in teams:
			killedInThatTeam = min(t.count, count // len(teams))
			t.count = t.count - killedInThatTeam
			debug("%d ppl removed from team %s" % (killedInThatTeam, t.nato))
			leftToKill = leftToKill - killedInThatTeam

		if leftToKill > 0 and len(teams) > 1: # if one team, we didn't divide, so there is no way there are ppl left to kill
			debug("we need to remove more ppl")
			for t in teams:
				killedInThatTeam = min(t.count, leftToKill)
				t.count = t.count - killedInThatTeam
				debug("%d ppl removed from team %s" % (killedInThatTeam, t.nato))
				leftToKill = leftToKill - killedInThatTeam
				if leftToKill == 0:
					break

	def updateCommandList(self, t):
		if not t.fighting:
			c = [c for c in t.commands.list if isinstance(t, CommandFight)]
			if len(c) == 0:
				t.commands.add(CommandFight(t.count))
				debug("adding task fight for team %s" % t.nato)
				t.fighting = True

		t.stillFighting = True

	def fight(self, t1, t2):
		debug("Fight between:")
		for t in t1:
			self.updateCommandList(t)
			debug("on my left: %s" % t.nato)

		for t in t2:
			self.updateCommandList(t)
			debug("on my right: %s" % t.nato)

		count1 = sum([t.count for t in t1])
		count2 = sum([t.count for t in t2])
		if count1 > 0 and count2 > 0:
			killedBy_1 = min(count2, random.randrange(0, count1))
			killedBy_2 = min(count1, random.randrange(0, count2))
			debug("left team will kill %d ppl" % killedBy_1)
			debug("right team will kill %d ppl" % killedBy_2)
			self.kill(t2, killedBy_1)
			self.kill(t1, killedBy_2)

	def buildListOnThatCell(self, teams, x, y):
		r = []
		temp = copy.copy(teams)
		while len(temp) > 0:
			t = temp.pop()
			if t.x == x and t.y == y:
				r.append(t)
		return r

	def getAliveCount(self, teams):
		return sum([t.count for t in teams])

	def run(self):
		temp = copy.copy(self.teams1)
		while len(temp) > 0:
			t = temp.pop()
			t1 = self.buildListOnThatCell(self.teams1, t.x, t.y)
			t2 = self.buildListOnThatCell(self.teams2, t.x, t.y)
			if self.getAliveCount(t2) > 0 and self.getAliveCount(t1) > 0: # t1 team could be all dead
				self.fight(t1, t2) 
		self.clean(self.teams1)
		self.clean(self.teams2)

	def clean(self, teams):
		for t in teams:
			if t.fighting and not t.stillFighting:
				debug("removing task fight for team %s" % t.nato)
				t.fighting = False
				c = [c for c in t.commands.list if isinstance(c, CommandFight)] # should exists
				if len(c) > 0:
					command = c[0]
					if t.getAlive():
						loss = command.countBefore - t.count
						if loss == 0:
							t.addReply("we just had a fight but we suffer no loss")
						elif loss == 1:
							t.addReply("we just had a fight and we lost one guy")
						else:
							t.addReply("we just had a fight and we lost %d peoples" % (command.countBefore - t.count))
					if len(c) > 0:
						t.commands.list.remove(command) 

class TimedFight():
	def __init__(self):
		self.lastFightTime = datetime.datetime.now()

	def check(self, map_, teams1, teams2):
		if self.lastFightTime + datetime.timedelta(seconds = 10 / SPEED_FACTOR) < datetime.datetime.now(): # every 10 minutes in game
			self.lastFightTime = datetime.datetime.now() 
			Fight(map_, teams1, teams2).run() # will also handle the command
