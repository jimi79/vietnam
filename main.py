import datetime
import curses

from const import *
from map import *
from team import *
from teams import *
from goals import *
from query import *

class Main():

	def init_curses(self):
		curses.initscr()
		curses.start_color()
		#curses.use_default_colors()
		curses.curs_set(0)
		#curses.cbreak()
		#curses.halfdelay(1) #nocbreak to cancel
		curses.init_pair(COLOR_WATER, curses.COLOR_WHITE, curses.COLOR_BLUE)
		curses.init_pair(COLOR_FOREST, curses.COLOR_BLACK, curses.COLOR_GREEN)

	def __init__(self):
		self.init_curses()
		self.map = Map_()
		self.map.place()
		self.query_win = curses.newwin(1, 60, 0, 0)
		self.log_win = curses.newwin(10, 120, 2, 0)
		self.log_win.scrollok(True)
		self.debug_win = curses.newwin(11, 12, 15, 0) # display the map, cheat
		self.help_win = curses.newwin(10, 30, 0, 125)
		self.player_teams = Teams(COUNT_PLAYER_TEAMS, self.map)
		self.npc_teams = Teams(COUNT_NPC_TEAMS, self.map) 
		self.player_teams.set_other_team(self.npc_teams)
		self.npc_teams.set_other_team(self.player_teams)
		self.goals = Goals() # a list of places, and place on the map the first one to reach 
		self.initial_time = None

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

	def get_key(self):
		curses.halfdelay(10) #nocbreak to cancel
		try:
			key = self.query_win.getch()
		except:
			return None
		return key

	def get_replies(self):
		return self.player_teams.get_replies()

	def update_query(self, query):
		self.help_win.clear()
		self.help_win.addstr(query.get_help()) # todo get_help
		self.help_win.refresh()
		self.query_win.clear()
		self.query_win.addstr(query.get_text()) 
		self.help_win.refresh()

	def add_log(self, text, title = None):
		if title == None:
			self.log_win.addstr("  %s\n%s\n" % (self.get_time(), text))
		else:
			self.log_win.addstr("  %s, %s\n%s\n" % (self.get_time(), title, text))
		self.log_win.refresh()

	def get_time(self):
		d = (datetime.datetime.now() - self.initial_time).seconds
		#d = d / 10
		d = d * SPEED_FACTOR
		day = d // (24 * 60)
		d = d % (24 * 60) 
		return "day %d %02d:%02d" % (day + 1, d // 60, d % 60)

	def run(self, stdscr): 
		query = Query(self.player_teams)
		self.help_win.clear()
		self.help_win.addstr(query.get_help()) # todo get_help
		self.help_win.refresh()
		k = None
		self.initial_time = datetime.datetime.now()
		while True:
			if DEBUG: 
				self.print_map(self.debug_win)
			k = self.get_key()
			open("log3", "w").write("%d" % k)
			if k == ord('Q'):
				break
			if k != -1:
				if k == 27:
					query.init()
					self.update_query(query)
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
