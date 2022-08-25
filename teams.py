import json
from team import *
from command import *
from const import *


class Teams():
	def add(self, team, npc, map_):
		if npc:
			locations = map_.getTeamNpcPatrolLocation(team.y, team.x)
			if len(locations) > 0:
				team.commands.add(CommandPatrol(locations, team.y, team.x)) 
		team.npc = npc
		team.ourTeams = self 
		team.map = map_
		self.list.append(team) 

	def rand(self, params):
		diff = random.randrange(0, params[1])
		val = params[0] - params[1] // 2 + diff
		return val

	def __init__(self, count, map_, npc, goals):
		self.list = []
		self.nato =['alpha', 'bravo', 'charly', 'delta', 'echo', 'fox-trot', 'hotel', 'india', 'juliet', 'kilo', 'lima', 'mike', 'november', 'oscar', 'papa', 'quebec', 'romeo', 'sierra', 'tango', 'uniform', 'victor', 'wiskhey', 'x-ray', 'yankee', 'zulu']
		self.npcId = 0
		for i in range(0, count):
			if npc:
				members = self.rand(NPC_TEAMS_AVG_SIZE)
			else:
				members = self.rand(PLAYER_TEAMS_AVG_SIZE)
			if not npc:
				if SUPERMAN:
					members = 100
			if npc:
				y, x = map_.getTeamNpcLocation()
			else: 
				y, x = map_.getTeamPlayerLocation()
			if npc:
				self.npcId = self.npcId + 1
				name = str(i) 
			else:
				name = self.nato.pop(0)
			t = TeamInfantry(id_ = i, count = members, goals = goals, y = y, x = x, name = name) 
			self.add(t, npc, map_)

	def appendHeli(self, map_, npc):
		name = self.nato.pop(0)
		heli = TeamHelicopter(len(self.list), name = name)
		self.add(heli, npc, map_)

	def getChar(self, y, x):
		for team in [t for t in self.list if isinstance(t, TeamInfantry)]:
			if team.x == x and team.y == y:
				return True
		return False

	def setOtherTeam(self, otherTeams):
		for t in self.list:
			t.otherTeams = otherTeams
	
	def setOurTeams(self, ourTeams):
		for t in self.list:
			t.ourTeams = ourTeams

	def tick(self):
		for t in self.list:
			t.tick()

	def getTeamByLetter(self, id_):
		a = [team for team in self.list if team.id == id_]	
		if len(a) == 0:
			return None
		else:
			return a[0]

	def apply(self, query):
		action = ParseQueryToCommand().parse(query) 
		for t in self.list:
			if t.id == action.id:
				t.commands.add(action)
				break
	
	def getReplies(self):
		replies = []
		for team in self.list:
			replies = replies + team.dumpReplies()
		return replies

	def getInfrantryList(self):
		lst = [team for team in self.list if isinstance(team, TeamInfantry)]
		return lst

	def getAllTeamsStatus(self):
# all infantry teams, helico is untouchable anyway
		r = []
		infantryTeams = self.getInfrantryList()
		aliveTeams = [team for team in infantryTeams if team.getAlive()]
		exitedTeams = [team for team in infantryTeams if team.exited]
		if len(aliveTeams) != len(infantryTeams):
			r.append(ONE_TEAM_DEAD)
		if len(aliveTeams) == 0:
			r.append(ALL_TEAMS_DEAD)
		if len(exitedTeams) == len(aliveTeams) and len(aliveTeams) > 0:
			r.append(ALL_ALIVE_TEAMS_EXITED)
		if len(exitedTeams) == len(infantryTeams):
			r.append(ALL_TEAMS_EXITED)
		return r

	def getDebugInfos(self):
		l = []
		for t in self.list:
			if isinstance(t, TeamInfantry):
				l.append("%s: %d alive (y=%d, x=%d)" % (t.nato, t.count, t.y, t.x))
			if isinstance(t, TeamHelicopter):
				l.append("heli %s" % (t.nato))
		return l
