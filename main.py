import datetime
import curses
import time

from const import *
from map import *
from team import *
from teams import *
from goals import *
from query import *
from fight import *

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
		curses.init_pair(1, 0, curses.COLOR_GREEN)
		curses.init_pair(2, 0, curses.COLOR_BLUE)

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
			self.old_y = y
			self.old_x = x
			self.query_win.resize(1, x)
			self.query_win.mvwin(y - 2, 0)
			self.log_win.resize(y - 2, x)
			self.log_win.mvwin(0, 0)
			self.query_win.refresh()
			self.log_win.refresh()

	def init_game(self):
		self.map = Map_()
		self.map.place(count_forest = COUNT_FOREST, count_wonder = COUNT_WONDER, count_water = COUNT_WATER)
		self.goals = Goals(self.map) # a list of places, and place on the map the first one to reach 
		self.player_teams = Teams(count = COUNT_PLAYER_TEAMS, map_ = self.map, npc = False, goals = self.goals)
		self.player_teams.append_heli(map_ = self.map, npc = False)
		self.npc_teams = Teams(count = COUNT_NPC_TEAMS, map_ = self.map, npc = True, goals = self.goals) 
		self.player_teams.set_other_team(self.npc_teams)
		self.npc_teams.set_other_team(self.player_teams)
		self.initial_time = datetime.datetime.now()
		self.last_fight_time = datetime.datetime.now() # should be in Fight object, and that object should be instanciated from the beginning

	def init(self, stdscr):
		self.init_windows(stdscr)
		self.init_game()

	def tick(self, stdscr):
		if self.last_fight_time + datetime.timedelta(seconds = 10 / SPEED_FACTOR) < datetime.datetime.now(): # every 10 minutes in game
			self.last_fight_time = datetime.datetime.now()
			Fight(self.map, self.player_teams, self.npc_teams).run() # will also handle the command

		self.player_teams.tick()
		self.npc_teams.tick()


		for reply in self.get_replies():
			self.add_log("%s: %s" % (reply.team, reply.text))
		a = self.get_all_teams_status()

		end = False
		if ALL_ALIVE_TEAMS_EXITED in a:
			self.add_log('All alive units are safe. Press a key to exit')
			end = True

		if end:
			curses.cbreak() #nocbreak to cancel
			a = stdscr.getch() # no halfkey here
			return False

		return True


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
		self.query_win.clear()
		self.query_win.addstr(query.get_text()) 
		self.query_win.refresh()
	
	def get_help(self, query):
		self.add_wrap(self.log_win, ', '.join(query.get_help())) 
	
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

	def add_log(self, text, shift = 0):
		text = "%s: %s" % (self.get_time(), text)
		text = ''.join([' ' for a in range(0, shift)]) + text
		self.add_wrap(self.log_win, text) 

	def log_goals(self):
		if DEBUG:
			for goal in self.goals.list:
				self.add_log("%s at (%d, %d), done:%s, duration: %0.0f" % (goal.name, goal.y, goal.x, "True" if goal.done else "False", goal.duration)) 

	def get_time(self):
		d = (datetime.datetime.now() - self.initial_time).total_seconds()
		#d = d / 10
		d = d * SPEED_FACTOR
		day = d // (24 * 60)
		d = d % (24 * 60) 
		return "day %d %02d:%02d" % (day + 1, d // 60, d % 60)

	def get_all_teams_status(self):
		return self.player_teams.get_all_teams_status()

	def log_status(self):
		a = self.get_all_teams_status()
		self.add_log(", ".join(a))
	
	def log_locations(self):
		p = "player: %s" % ", ".join(self.player_teams.get_debug_infos())
		n = "npc: %s" % ", ".join(self.npc_teams.get_debug_infos())
		self.add_log("%s\n%s" % (p, n))
	
	def log_tasks(self):
		s = []
		s.append("Player's teams:")
		for team in self.player_teams.list:
			s.append("%s: %s" % (team.nato, team.commands.debug()))
		s.append("NPC's teams:")
		for team in self.npc_teams.list:
			s.append("%s: %s" % (team.nato, team.commands.debug()))
		self.add_log("\n".join(s)) 

	def run(self, stdscr): 
		self.init(stdscr) 

		query = Query(self.player_teams)
		self.update_query(query)
		k = None

		old_time = datetime.datetime.now()
		while True:
			#self.update_time()
			time = datetime.datetime.now()
			if (time - old_time).total_seconds() > 1: 
				if not self.tick(stdscr):
					break
				old_time = time 
				self.resize_windows(stdscr)

			k = self.get_key(stdscr)
			if k != None:
				if DEBUG:
					if k == ord('1'):
						self.log_goals() 
					elif k == ord('2'):
						self.log_status()
					elif k == ord('3'):
						self.log_locations()
					elif k == ord('4'):
						self.log_tasks() 
					elif k == ord('5'):
						self.print_map(self.log_win) 

				if k == ord('Q'):
					if self.confirm(stdscr):
						break
					else:
						self.update_query(query)
				elif k == ord('\t'):
					self.get_help(query)
				elif k == curses.KEY_BACKSPACE:
					query.delete_last()
					self.update_query(query)
				elif k == 27:
					query.init()
					self.update_query(query)
				else:
					k = chr(k)
					state = query.test_key(k)
					if state != QUERY_ERR: 
						if state == QUERY_DONE:
							self.player_teams.apply(query)
							self.add_log('you: %s' % query.get_text(), shift=2)
							query.init()
						self.update_query(query)
