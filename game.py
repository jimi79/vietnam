#!/usr/bin/python3

import curses
import time
import datetime
import random
import json


# forest: invisible but can't see
# moving: defence = 0.5
# defending: defence = 1
# how to make water super dangerous, but still crossable in case random doesn't make the map possible?


FOREST = "F"
WATER = "W"
BORDER = "B"
NOTHING = "N"
ENNEMIES = "E"
COLOR_NONE = 0
COLOR_WATER = 1
COLOR_FOREST = 2

STATE_DEFEND = 0
STATE_MOVING = 1
STATE_WORKING = 3

COMMAND_LOOK = "LOOK"
COMMAND_MOVE = "MOVE"
COMMAND_DEFEND = "DEFEND"
COMMAND_WORK = "WORK"

QUERY_DONE = 2 # query complete, could be executed
QUERY_ERR = 1 # key not authorized
QUERY_NEXT = 0 # query not complete

SIZE = 10

COUNT_PLAYER_TEAMS = 1
COUNT_NPC_TEAMS = 3

SECONDS_PER_CELL = 15 # time in second to go from one cell to another. if moving in diagonal, take that time * sqr(2)

def rnd():
	return random.randrange(0, SIZE) 

class Map_():
	def __init__(self):
		self.geo = [[None for i in range(0, SIZE)] for j in range(0, SIZE)]

	def get_color(self, y, x):
		if self.geo[y][x] == None:
			return COLOR_NONE
		if self.geo[y][x] == FOREST:
			return COLOR_FOREST
		if self.geo[y][x] == WATER:
			return COLOR_WATER

	def randomize(self):
		for i in range(0, SIZE):
			self.geo[rnd()][rnd()] = FOREST
		for i in range(0, SIZE):
			self.geo[rnd()][rnd()] = WATER

class Mission():
	pass

class Load():
	pass
	#init mission and map accordingly
# if no map definition, then auto generate it

class Team():
	def __init__(self, id_, count, map_): 
		self.count = count
		self.last_state_date = datetime.datetime.now()
		self.id = id_
		self.map = map_
		self.other_teams = None 
		while True:
			self.y = rnd()
			self.x = rnd()
			if self.map.geo[self.y][self.x] != WATER:
				break
		self.state = STATE_DEFEND
		self.dest_x = None
		self.dest_y = None
	
	def get_str(self, type_, previous_items):
# get random string for each type.
# if string already said, we say 'another' in front
		pass

	def get_pos_from_direction(self, direction):
		y = self.y + (1 if "S" in direction else -1 if "N" in direction else 0)	
		x = self.x + (1 if "E" in direction else -1 if "W" in direction else 0)	
		return y, x 

	def get_item_at_pos(self, direction):
# meanwhile, perhaps do it simple.
# like just return into l a list, without 'a' or what, and then construct it

# out of bound=border
		y, x = self.get_pos_from_direction(direction)
	
		#print("%d, %d" % (y, x))
		if x < 0 or y < 0 or x >= SIZE or y >= SIZE:
			s = "a border"
		else: 
			s = ""
			if self.map.geo[y][x] == FOREST:
				s = "a forest"
			if self.map.geo[y][x] == WATER:
				s = "some water"
			if self.other_teams != None:
				c = 0
				c = sum([a.count for a in self.other_teams.list if a.x == x and a.y == y])
				if c > 0:
					if s != "":
						s = s + " and "
					if c > 10:
						s = s + "lots of soldiers" 
					else:
						s = s + "some soldiers" 
		
		if s != "":
			txt = "%s: %s" % (direction, s)
		else:
			txt = None
		return txt

	def get_ennemies_at_pos(self, direction): 
		x, y = self.get_pos_from_direction(direction)
		teams = [team for team in self.other_teams if team.x == x and team.y == y]
		print(teams)
			
	
	def look(self): 
# save the map in some file to check, i doubt the display now
# add some details in that log
		items = [] 
		for d in ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]:
			item = self.get_item_at_pos(d)
			#item2 = self.get_ennemies_at_pos(d) # sum of bad guys
			if item != None:
				items.append(item)

		return ', '.join(items)

	def act(self):
		pass
		# if moving, continue if possible
# if same cell as ennemy, attack
# etc
# i need a diagram for that

# grammar: no mention if nothing
# synonym
# another if alreayd mentionned
# from x to y if forest continuing (i need a list to do that maybe, like to regroup)
			
			

class Teams():
	def __init__(self, count, map_):
		self.list = []
		for i in range(0, count):
			t = Team(i + 1, 2, map_)
			self.list.append(t)

	def get_char(self, y, x):
		for team in self.list:
			if team.x == x and team.y == y:
				return True
		return False

	def get_list(self):
		return [a.id for a in self.list]

	def set_other_team(self, other_teams):
		for t in self.list:
			t.other_teams = other_teams

class Query():
	def init(self):
		self.pos = {
			'name': 'team', 
			'values': 
				{str(a): {
					'text': 'Team %d' % a, 'code': a
				} for a in self.teams.get_list()
			}
		}
		self.query = [] # current query
		self.end = False

	def __init__(self, teams):
		self.teams = teams
		self.init() 

	def get_text(self):
		txt = [item['text'] for item in self.query]
		return ' '.join(txt)

	def get_help(self): 
		values = self.pos['values']
		lst = ["%s: %s" % (key, values[key]['text']) for key in values.keys()]
		return "\n".join(lst)

	def next_query(self):
		if len(self.query) == 1:
			self.pos = {
				'name': 'action', 
				'values': 
					{
						'l': {'text': 'look', 'code': COMMAND_LOOK},
						'd': {'text': 'defend', 'code': COMMAND_DEFEND},
						#'w': {'text': 'work', 'code': COMMAND_DEFEND} #only if available, i need the map here, or some goal object, not sure. i think the map though, which will have a goal object
						'm': {'text': 'move', 'code': COMMAND_MOVE}
					}
				}

		if len(self.query) == 2:
			if self.query[-1]['code'] == COMMAND_LOOK:
				self.end = True
			if self.query[-1]['code'] == COMMAND_DEFEND:
				self.end = True 
			if self.query[-1]['code'] == COMMAND_WORK:
				self.end = True
			if self.query[-1]['code'] == COMMAND_MOVE:
				self.pos = {
					'name': 'direction', 
					'values': 
						{
							'w': {'text': 'north', 'code': 'n'},
							'e': {'text': 'north east', 'code': 'ne'},
							'd': {'text': 'east', 'code': 'e'},
							'c': {'text': 'south east', 'code': 'se'},
							'x': {'text': 'south', 'code': 's'},
							'z': {'text': 'south west', 'code': 'sw'},
							'a': {'text': 'west', 'code': 'w'},
							'q': {'text': 'north west', 'code': 'nw'}
						}
					}
		if len(self.query) == 3:
			self.end = True



	def test_key(self, key): 
		if not self.end:
			if key in self.pos['values'].keys():
				self.query.append(
					{
						'code': self.pos['values'][key]['code'],
						'text': self.pos['values'][key]['text']
					})
				self.next_query()
				if self.end:
					return QUERY_DONE
				else:
					return QUERY_NEXT
			else:
				return QUERY_ERR
		else:
			return QUERY_ERR

class Goals():
	def __init__(self):
		pass
# list of places, with a description (random?) and a time to work there

class Main():

	def init_curses(self):
		curses.initscr()
		curses.start_color()
		#curses.use_default_colors()
		curses.curs_set(0)
		#curses.cbreak()
		curses.halfdelay(SIZE) #nocbreak to cancel
		curses.init_pair(COLOR_WATER, curses.COLOR_WHITE, curses.COLOR_BLUE)
		curses.init_pair(COLOR_FOREST, curses.COLOR_BLACK, curses.COLOR_GREEN)

	def __init__(self):
		self.init_curses()
		self.map = Map_()
		self.map.randomize()
		self.query_win = curses.newwin(1, 60, 0, 0)
		self.log_win = curses.newwin(10, 60, 2, 0)
		self.log_win.scrollok(True)
		self.debug_win = curses.newwin(11, 12, 15, 0) # display the map, cheat
		self.help_win = curses.newwin(10, 30, 0, 62)
		self.player_teams = Teams(COUNT_PLAYER_TEAMS, self.map)
		self.npc_teams = Teams(COUNT_NPC_TEAMS, self.map)

		self.player_teams.set_other_team(self.npc_teams)
		self.npc_teams.set_other_team(self.player_teams)
		self.goals = Goals() # a list of places, and place on the map the first one to reach

	def print_map(self, win):
		for y in range(0, SIZE):
			for x in range(0, SIZE):
				c = self.map.get_color(y, x)
				ch = ' '
				if self.npc_teams.get_char(y, x):
					ch = 'N'
				if self.player_teams.get_char(y, x):
					ch = 'P'
				win.addstr(ch, curses.color_pair(c)) 
			win.addstr("\n")
		win.refresh()

	def get_key(self):
		key = None
		try:
			key = self.query_win.getch()
		except:
			pass
		return key

	def update_query(self, query):
		self.help_win.clear()
		self.help_win.addstr(query.get_help()) # todo get_help
		self.help_win.refresh()
		self.query_win.clear()
		self.query_win.addstr(query.get_text()) 


	def run(self, stdscr): 
		query = Query(self.player_teams)
		k = None
		self.print_map(self.debug_win)
		look = self.player_teams.list[0].look()
		self.log_win.addstr("%s\n" % look)
		self.log_win.refresh()

		self.help_win.clear()
		self.help_win.addstr(query.get_help()) # todo get_help
		self.help_win.refresh()

		while True:
# print possibilities like key:value
			k = self.get_key()
			if k == ord('Q'):
				break
			if k != None:
				if k == 27:
					query.init()
					self.update_query(query)
				k = chr(k)
				if query.test_key(k) != QUERY_ERR:
					self.update_query(query)
					self.log_win.addstr(json.dumps(query.pos))
					self.log_win.refresh()
#update query display

# i need a new window to show the help for the completion

#			print(query.get_text())
#			self.log_win.addstr(query.get_text())
#			self.log_win.refresh()
#			self.debug_win.addstr(0, 0, datetime.datetime.now().strftime("%s"))
#			self.debug_win.refresh()


def test_query(): 
	q = Query(Teams(2, Map_()))
	assert q.test_key('2') == QUERY_NEXT
	assert q.test_key('L') == QUERY_DONE
	print(q.query)

	q = Query(Teams(2, Map_()))
	assert q.test_key('1') == QUERY_NEXT
	assert q.test_key('M') == QUERY_NEXT
	assert q.test_key('w') == QUERY_DONE
	print(q.query)

def run():
	m = Main()
	curses.wrapper(m.run)
		
run()
