from team import *
from command import *
from pprint import pformat
import json


class Teams():
	def __init__(self, count, map_, npc, goals):
		self.list = []
		for i in range(0, count):
			members = random.randrange(5, 15)
			if DEBUG:
				if not npc:
					members = 100
			if npc:
				y, x = map_.get_team_npc_location()
			else: 
				y, x = map_.get_team_player_location()
			t = Team(id_ = i, count = members, map_ = map_, goals = goals, y = y, x = x) 
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

	def is_end_game(self):
		return len([team for team in self.list if team.win]) == len(self.list)
