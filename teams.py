from team import *
from command import *
from pprint import pformat
from const import *
import json


class Teams():
	def __init__(self, count, map_, npc, goals):
		self.list = []
		for i in range(0, count):
			if npc:
				log('adding team %d' % i)
			members = random.randrange(5, 15)
			if not npc:
				if SUPERMAN:
					members = 100
			if npc:
				y, x = map_.get_team_npc_location()
			else: 
				y, x = map_.get_team_player_location()
			t = Team(id_ = i, count = members, map_ = map_, goals = goals, y = y, x = x) 
			if npc:
				locations = map_.get_team_npc_patrol_location(y, x)
				if len(locations) > 0:
					t.apply(CommandPatrol(locations, y, x)) 
			t.npc = npc
			t.our_teams = self


			self.list.append(t)

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

	def apply(self, query):
		action = ParseQueryToCommand().parse(query) 
		for t in self.list:
			if t.id == action.id:
				t.apply(action)
	
	def get_replies(self):
		replies = []
		for team in self.list:
			replies = replies + team.dump_replies()
		return replies

	def get_all_teams_status(self):
		r = []
		alive_teams = [team for team in self.list if team.get_alive()]
		exited_teams = [team for team in self.list if team.exited]
		if len(alive_teams) != len(self.list):
			r.append(ONE_TEAM_DEAD)
		if len(alive_teams) == 0:
			r.append(ALL_TEAMS_DEAD)
		if len(exited_teams) == len(alive_teams) and len(alive_teams) > 0:
			r.append(ALL_ALIVE_TEAMS_EXITED)
		if len(exited_teams) == len(self.list):
			r.append(ALL_TEAMS_EXITED)
		return r

	def get_debug_infos(self):
		l = []
		for t in self.list:
			l.append("%s: %d alive (y=%d, x=%d)" % (t.nato, t.count, t.y, t.x))
		return l
