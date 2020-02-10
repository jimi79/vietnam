from const import *
from team import *
import time

class Log():
	def __init__(self):
		self.date = None
		self.delimiter = "--------------------------------"
		self.truncated = False
		self.list_teams_fighting = ""

	def new_fight(self, player_teams):
		t = [t.nato for t in player_teams.list if isinstance(t, TeamInfantry) and t.get_alive() and t.fighting]
		list_teams_fighting = ', '.join(t)
		if list_teams_fighting != self.list_teams_fighting:
			self.list_teams_fighting = list_teams_fighting
			return True
		return False

	def needs_update(self, player_teams):
		delay = 0
		date = datetime.datetime.now()
		if self.date != None:
			delay = (date - self.date).total_seconds() * SPEED_FACTOR 
		return (self.date == None) or (delay > 30) or (self.new_fight(player_teams))

	def add_log(self, stime, map_, player_teams, npc_teams, goals, term):
		# if date is more than xx seconds / speed thing, then log
		if not self.truncated: 
			self.truncated = True
			open("log", "w").close() # i assume that truncates

		self.date = datetime.datetime.now()
		s = self.delimiter + '\n'
		s = s + "%s\n" % stime
		for y in range(0, SIZE):
			for x in range(0, SIZE):
				if map_.geo[y][x] == None:
					c = "\033[0m"
				elif map_.geo[y][x] == FOREST: 
					c = "\033[48;5;22m" 
				elif map_.geo[y][x] == WATER: 
					c = "\033[48;5;21m" 

				ch = ' ' 

				for g in goals.list:
					if g.x == x and g.y == y:
						if isinstance(g, EndGoal):
							ch = 'E'
						else:
							if not g.done:
								ch = 'G'

				if len([t for t in npc_teams.list if isinstance(t, TeamInfantry) and t.x == x and t.y == y and t.get_exists()]) > 0:
					ch = '+'

				l = [t for t in player_teams.list if isinstance(t, TeamInfantry) and t.x == x and t.y == y and t.get_exists()]
				if len(l) > 0:
					ch = l[0].letter
					
				if len([t for t in player_teams.list if isinstance(t, TeamInfantry) and t.x == x and t.y == y and t.get_alive() and t.fighting]) > 0:
					c = "\033[48;5;196m" 
					ch = '*'

				s = s + c + ch
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
