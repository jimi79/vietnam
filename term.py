import curses
import datetime
from const import *


class WindowHandler():
	def __init__(self):
		pass
	

PLAYER_WINDOW = 1
TEAM_WINDOW = 2
HORZ = 0
VERT = 1
QUAD = 2

def log(text):
	open("test", "a").write("%s\n" % text)

class Window():
	def __init__(self, index, class_, window):
		self.index = index
		self.class_ = class_
		self.log = []
		self.window = window 
		self.window.scrollok(True)

	def add_wrap(self, text):
		win = self.window
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
		win.refresh()

	def refill(self):
		self.window.clear()
		for l in self.log:
			self.add_wrap(l) 

	def add_text(self, text): 
		#self.log = self.log[-100:]
		self.log.append(text)
		self.add_wrap(text)

class WindowHandler():
	def __init__(self, stdscr, teams):
		self.team_windows = []
		self.stdscr = stdscr
		self.teams = teams
		self.old_x = 0
		self.old_y = 0
		self.query = ""
		self.init()

	def init(self):
		index = 0
		y, x = self.stdscr.getmaxyx() 
		for team in self.teams.list:
			window = Window(index, TEAM_WINDOW, curses.newwin(1, x, index, 0))
			index = index + 1 
			self.team_windows.append(window)
			team.window = window
		window = curses.newwin(1, x, index, 0)
		self.query_win = Window(index, PLAYER_WINDOW, window)
		self.layout = HORZ
		self.resize()

	def resize(self):
		y, x = self.stdscr.getmaxyx() 
		if (y != self.old_y) or (x != self.old_x):
			self.stdscr.clear()
			self.stdscr.refresh()
			self.old_x = x
			self.old_y = y
			if self.layout == HORZ:
				self.query_win.window.resize(2, x)
				self.query_win.window.mvwin(y - 2, 0)
				y = y - 1 # what's left of the screen
				height_per_win = int(y / 4)
				top = 0
				for window in self.team_windows:
					window.window.resize(height_per_win, x)
					window.window.mvwin(window.index * height_per_win, 0) 
					window.refill() 
			else:
				raise Exception("not handled")
			self.update_query(self.query)
	
	def add_text(self, window, text):
		window.add_text(text)

	def update_query(self, text):
		self.query = ""
		self.query_win.window.clear()
		self.query_win.window.addstr(text)
		self.query_win.window.refresh() 
		self.query_win.window.addstr("test")

class Term():
	def __init__(self, stdscr, teams):
		self.stdscr = stdscr
		curses.initscr()
		curses.start_color()
		#curses.use_default_colors()
		#curses.curs_set(0)
		#curses.cbreak()
		curses.halfdelay(10) #nocbreak to cancel
		curses.init_pair(1, 0, curses.COLOR_GREEN)
		curses.init_pair(2, 0, curses.COLOR_BLUE)
		self.initial_time = datetime.datetime.now()
		self.handler = WindowHandler(stdscr, teams)

	def get_time(self):
		d = (datetime.datetime.now() - self.initial_time).total_seconds()
		#d = d / 10
		d = d * SPEED_FACTOR
		day = d // (24 * 60)
		d = d % (24 * 60) 
		return "day %d %02d:%02d" % (day + 1, d // 60, d % 60) 

	def add_log(self, text, shift = 0, team = None):
		text = "%s: %s" % (self.get_time(), text)
		text = ''.join([' ' for a in range(0, shift)]) + text
		if team is None:
			for win in self.handler.team_windows:
				self.handler.add_text(win, text)
		else:
			self.handler.add_text(team.window, text)

	def update_query(self, text):
		self.handler.update_query(text)

	def resize(self):
		self.handler.resize()
