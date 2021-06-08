from const import *
from team import *
import time

class Log():
	def __init__(self):
		self.date = None
		self.delimiter = "--------------------------------"
		self.truncated = False
		self.fights = []
		self.positions = []
		self.goals = []

	def fight_change(self, player_teams):
		current_fights = [t.nato for t in player_teams.list if isinstance(t, TeamInfantry) and t.get_alive() and t.fighting]
		if current_fights != self.fights:
			self.fights = current_fights
			return True
		else:
			return False

	def position_changed(self, player_teams):
		current_positions = []
		for team in player_teams.list:
			if isinstance(team, TeamInfantry):
				if not(team.exited):
					current_positions.append([team.x, team.y])
		if self.positions != current_positions:
			self.positions = current_positions
			return True
		else:
			return False 

	def goal_changed(self, goals):
		current_goals = [g.name for g in goals.list if (not(g.done))]
		if self.goals == []:
			self.goals = current_goals
		if current_goals != self.goals:
			self.goals = current_goals
			return True
		else:
			return False 

	def get_update_reason(self, player_teams, goals):
		if self.fight_change(player_teams): 
			return "Fight update"
		if self.goal_changed(goals):
			return "Goal achived"
		if self.position_changed(player_teams):
			return "Position update"
		return None

	def add_log(self, stime, map_, player_teams, npc_teams, goals, update_reason, term):
		# if date is more than xx seconds / speed thing, then log
		if not self.truncated:
			self.truncated = True
			open("log", "w").close() # i assume that truncates

		self.date = datetime.datetime.now()
		s = self.delimiter + '\n'
		s = s + "%s, %s\n" % (stime, update_reason)
		for y in range(0, SIZE):
			for x in range(0, SIZE):
				if map_.geo[y][x] == None:
					c = "\033[0m"
				elif map_.geo[y][x] == FOREST:
					c = "\033[48;5;22m"
				elif map_.geo[y][x] == WATER:
					c = "\033[48;5;21m"

				good_guys = " "
				bad_guys = " "
				goal = " "

				for g in goals.list:
					if g.x == x and g.y == y:
						if isinstance(g, EndGoal):
							goal = 'E'
						else:
							if not g.done:
								goal = 'G'

				if len([t for t in npc_teams.list if isinstance(t, TeamInfantry) and t.x == x and t.y == y and t.get_exists()]) > 0:
					bad_guys = '+'

				l = [t for t in player_teams.list if isinstance(t, TeamInfantry) and t.x == x and t.y == y and t.get_exists()]
				if len(l) > 0:
					good_guys = l[0].letter

				if len([t for t in player_teams.list if isinstance(t, TeamInfantry) and t.x == x and t.y == y and t.get_alive() and t.fighting]) > 0:
					c = "\033[48;5;196m"

				s = s + c + good_guys + bad_guys + goal
			s = s + '\033[0m\n'
		f = open("log", "a")
		f.write(s)
		f.close()

	def replay(self, speed):
		if speed == None:
			speed = 1
		print("\033[2J\033[1;1H", end = "")
		f = open("log", "r")
		first_delimiter = True
		while True:
			line = f.readline()
			if not line:
				break
			if line.strip() == self.delimiter:
				if not first_delimiter:
					time.sleep(1 / speed)
				else:
					first_delimiter = False
				print("\033[2J\033[1;1H", end = "")
			else:
				print(line, end = "")
