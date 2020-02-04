import json
from team import *
from command import *
from const import *


class Teams():
	def add(self, team, npc, map_):
		if npc:
			locations = map_.get_team_npc_patrol_location(team.y, team.x)
			if len(locations) > 0:
				team.commands.add(CommandPatrol(locations, team.y, team.x)) 
		team.npc = npc
		team.our_teams = self 
		team.map = map_
		self.list.append(team) 

	def __init__(self, count, map_, npc, goals):
		self.list = []
		for i in range(0, count):
			members = random.randrange(5, 15)
			if not npc:
				if SUPERMAN:
					members = 100
			if npc:
				y, x = map_.get_team_npc_location()
			else: 
				y, x = map_.get_team_player_location()
			t = TeamInfantry(id_ = i, count = members, goals = goals, y = y, x = x) 
			self.add(t, npc, map_)

	def append_heli(self, map_, npc):
		heli = TeamHelicopter(len(self.list))
		self.add(heli, npc, map_)

	def get_char(self, y, x):
		for team in self.list:
			if team.x == x and team.y == y:
				return True
		return False

	def set_other_team(self, other_teams):
		for t in self.list:
			t.other_teams = other_teams
	
	def set_our_teams(self, our_teams):
		for t in self.list:
			t.our_teams = our_teams

	def tick(self):
		for t in self.list:
			t.tick()

	def get_team_by_letter(self, id_):
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
	
	def get_replies(self):
		replies = []
		for team in self.list:
			replies = replies + team.dump_replies()
		return replies

	def get_infrantry_list(self):
		lst = [team for team in self.list if isinstance(team, TeamInfantry)]
		return lst

	def get_all_teams_status(self):
# all infantry teams, helico is untouchable anyway
		r = []
		infantry_teams = self.get_infrantry_list()
		alive_teams = [team for team in infantry_teams if team.get_alive()]
		exited_teams = [team for team in infantry_teams if team.exited]
		if len(alive_teams) != len(infantry_teams):
			r.append(ONE_TEAM_DEAD)
		if len(alive_teams) == 0:
			r.append(ALL_TEAMS_DEAD)
		if len(exited_teams) == len(alive_teams) and len(alive_teams) > 0:
			r.append(ALL_ALIVE_TEAMS_EXITED)
		if len(exited_teams) == len(infantry_teams):
			r.append(ALL_TEAMS_EXITED)
		return r

	def get_debug_infos(self):
		l = []
		for t in self.list:
			if isinstance(t, TeamInfantry):
				l.append("%s: %d alive (y=%d, x=%d)" % (t.nato, t.count, t.y, t.x))
			if isinstance(t, TeamHelicopter):
				l.append("heli %s" % (t.nato))
		return l
