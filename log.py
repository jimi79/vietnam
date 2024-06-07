from const import *
from team import *
from writelog import *
import time

class Log():
	def __init__(self):
		self.date = None
		self.delimiter = "--------------------------------"
		self.truncated = False
		self.fights = []
		self.positions = []
		self.goals = []

	def fightChange(self, playerTeams):
		currentFights = [t.nato for t in playerTeams.list if isinstance(t, TeamInfantry) and t.getAlive() and t.fighting]
		if currentFights != self.fights:
			self.fights = currentFights
			return True
		else:
			return False

	def positionChanged(self, playerTeams):
		currentPositions = []
		for team in playerTeams.list:
			if isinstance(team, TeamInfantry):
				if not(team.exited):
					currentPositions.append([team.x, team.y])
		if self.positions != currentPositions:
			self.positions = currentPositions
			return True
		else:
			return False 

	def goalChanged(self, goals):
		currentGoals = [g.name for g in goals.list if (not(g.done))]
		if self.goals == []:
			self.goals = currentGoals
		if currentGoals != self.goals:
			self.goals = currentGoals
			return True
		else:
			return False 

	def getUpdateReason(self, playerTeams, goals):
		if self.fightChange(playerTeams): 
			return "Fight update"
		if self.goalChanged(goals):
			return "Goal achived"
		if self.positionChanged(playerTeams):
			return "Position update"
		return None

	def writeMap(self, map_, playerTeams, npcTeams, wonders, goals, updateReason, term):
		idWonder = 0
		wondersLegend = []
		s = ""
		for y in range(0, SIZE):
			for x in range(0, SIZE):
				if map_.geo[y][x] == None:
					c = "\033[0m"
				elif map_.geo[y][x] == FOREST:
					c = "\033[48;5;22m"
				elif map_.geo[y][x] == WATER:
					c = "\033[48;5;21m"

				goodGuys = " "
				badGuys = " "
				other = " "

				for w in wonders[0:10]:
					if w.x == x and w.y == y:
						idWonder = idWonder + 1
						other = str(idWonder)
						wondersLegend.append("%d: %s" % (idWonder, w.wonder.name))

				for g in goals.list:
					if g.x == x and g.y == y:
						if isinstance(g, EndGoal):
							other = 'E'
						else:
							if not g.done:
								other = 'G'

				if len([t for t in npcTeams.list if isinstance(t, TeamInfantry) and t.x == x and t.y == y and t.getExists()]) > 0:
					badGuys = '+'

				l = [t for t in playerTeams.list if isinstance(t, TeamInfantry) and t.x == x and t.y == y and t.getExists()]
				if len(l) > 0:
					goodGuys = l[0].letter

				if len([t for t in playerTeams.list if isinstance(t, TeamInfantry) and t.x == x and t.y == y and t.getAlive() and t.fighting]) > 0:
					c = "\033[48;5;196m"

				s += c + goodGuys + badGuys + other
			s += '\033[0m\n'
		s += "legend:\na: alpha\nb: bravo\nc: charly\nE: exit\nblue: water\ngreen: forest"
		s += "\n".join(wondersLegend)
		s += '\n'
		return s

	def writeLog(self, stime, map_, playerTeams, npcTeams, wonders, goals, updateReason, term):
		# if date is more than xx seconds / speed thing, then log
		if not self.truncated:
			self.truncated = True
			open("log", "w").close() # i assume that truncates

		self.date = datetime.datetime.now()
		s = self.delimiter + '\n'
		s = s + "%s, %s\n" % (stime, updateReason)
		s = s + self.writeMap(map_, playerTeams, npcTeams, wonders, goals, updateReason, term)
		self.write(s)

	def write(self, s):
		WriteLog().write(s)

	def replay(self, speed):
		if speed == None:
			speed = 1
		print("\033[2J\033[1;1H", end = "")
		f = open("log", "r")
		firstDelimiter = True
		while True:
			line = f.readline()
			if not line:
				break
			if line.strip() == self.delimiter:
				if not firstDelimiter:
					time.sleep(1 / speed)
				else:
					firstDelimiter = False
				print("\033[2J\033[1;1H", end = "")
			else:
				print(line, end = "")
