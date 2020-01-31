import datetime
import curses
import time

from const import *
from map import *
from team import *
from teams import *
from goals import *
from query import *

class Main():

	def confirm(self, stdscr): 
		self.query_win.clear()
		self.query_win.addstr('confirm closing (y/n)')
		self.query_win.refresh() 
		while True:
			curses.cbreak() #nocbreak to cancel
			a = stdscr.getkey()
			if a == 'y' or a == 'n':
				break
		return a == 'y' 

	def init_curses(self):
		curses.initscr()
		curses.start_color()
		#curses.use_default_colors()
		#curses.curs_set(0)
		#curses.cbreak()
		curses.halfdelay(10) #nocbreak to cancel
		#curses.init_pair(1, curses.COLOR_GRAY) # to display help

	def init_windows(self, stdscr):
		self.init_curses()
		y, x = stdscr.getmaxyx()
		self.query_win = curses.newwin(1, x, y - 2, 0)
		self.log_win = curses.newwin(y - 2, x, 0, 0)
		self.log_win.scrollok(True)
		self.old_y, self.old_x = (y, x)
	
	def resize_windows(self, stdscr):
		y, x = stdscr.getmaxyx()
		if y != self.old_y or x != self.old_x:
			self.log_win.addstr('resized to %d %d\n' % (y,x))
			self.old_y = y
			self.old_x = x
			self.query_win.resize(1, x)
			self.query_win.mvwin(y - 2, 0)
			self.log_win.resize(y - 2, x)
			self.log_win.mvwin(0, 0)
			self.log_win.addstr('after\n')
			self.query_win.refresh()
			self.log_win.refresh()

	def init_game(self):
		self.map = Map_()
		self.map.place(ratio_forest = RATIO_FOREST, ratio_wonder = RATIO_WONDER, ratio_water = RATIO_WATER)
		self.goals = Goals(self.map) # a list of places, and place on the map the first one to reach 
		self.player_teams = Teams(count = COUNT_PLAYER_TEAMS, map_ = self.map, npc = False, goals = self.goals)
		self.npc_teams = Teams(count = COUNT_NPC_TEAMS, map_ = self.map, npc = True, goals = self.goals) 
		self.player_teams.set_other_team(self.npc_teams)
		self.npc_teams.set_other_team(self.player_teams)
		self.initial_time = None 

	def init(self, stdscr):
		self.init_windows(stdscr)
		self.init_game()

	def tick(self):
		self.player_teams.tick()
		self.npc_teams.tick()

	def print_map(self, win):
		win.clear()
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

	def get_key(self, stdscr):
		curses.halfdelay(10) #nocbreak to cancel
		key = stdscr.getch()
		if key == -1:
			return None
		return key

	def get_replies(self):
		return self.player_teams.get_replies()

	def update_query(self, query):
#		self.help_win.clear()
#		self.help_win.addstr(query.get_help()) # todo get_help
#		self.help_win.refresh()
		self.query_win.clear()
		self.query_win.addstr(query.get_text()) 
		self.query_win.refresh()
	
	def get_help(self, query):
		#y, x = self.query_win.getyx() 
		self.add_log('\n'.join(query.get_help()))
		#self.query_win.move(y, x)
		self.query_win.refresh()

	
	def update_time(self):
		self.time_win.clear;
		self.time_win.addstr(0, 0, self.get_time())
		self.time_win.refresh()

	def add_wrap(self, win, text):
		words = text.split(" ")
		maxy, maxx = win.getmaxyx()
		for word in words:
			y, x = win.getyx()
			if len(word) + x > maxx:
				win.addstr("\n")
			win.addstr("%s " % word)
		y, x = win.getyx()
		if x != 0:
			win.addstr("\n")
		self.log_win.refresh() 

	def add_log(self, text, title = None):
		if title == None:
			self.add_wrap(self.log_win, "  -- %s --" % self.get_time())
		else:
			self.add_wrap(self.log_win, "  -- %s, %s --" % (self.get_time(), title))
		self.add_wrap(self.log_win, text) 

	def log_goals(self):
		if DEBUG:
			for goal in self.goals.list:
				self.add_log("%s at (%d, %d), done:%s, duration: %0.0f" % (goal.name, goal.y, goal.x, "True" if goal.done else "False", goal.duration))


	def get_time(self):
		d = (datetime.datetime.now() - self.initial_time).seconds
		#d = d / 10
		d = d * SPEED_FACTOR
		day = d // (24 * 60)
		d = d % (24 * 60) 
		return "day %d %02d:%02d" % (day + 1, d // 60, d % 60)

	def is_end_game(self):
		return self.player_teams.is_end_game()
	
	def run(self, stdscr): 
		self.init(stdscr) 

		query = Query(self.player_teams)
		self.update_query(query)
		k = None
		self.initial_time = datetime.datetime.now()

#		for team in self.player_teams.list:
#			self.add_log("Team %s: %d pp" % (team.nato, team.count))
#		for team in self.npc_teams.list:
#			self.add_log("Team %s: %d pp" % (team.nato, team.count))

		while True:
			#self.update_time()
			self.resize_windows(stdscr)
			k = self.get_key(stdscr)
			if k != None:
				if k == ord('Q'):
					if self.confirm(stdscr):
						break
					else:
						self.update_query(query)
				elif k == ord('\t'):
					self.get_help(query)
				elif k == ord('1'):
					self.log_goals()
				elif k == 27:
					query.init()
					self.update_query(query)
				else:
					k = chr(k)
					state = query.test_key(k)
					if state != QUERY_ERR: 
						if state == QUERY_DONE:
							self.player_teams.apply(query)
							self.add_log(query.get_text())
							query.init()
						self.update_query(query)
			self.tick()
			for reply in self.get_replies():
				self.add_log(reply.text, reply.team)
			if self.is_end_game():
				self.add_log('win, press a key')
				curses.cbreak() #nocbreak to cancel
				a = stdscr.getch() # no halfkey here
				break 
