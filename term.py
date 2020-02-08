import curses
import datetime
from const import *

class Term():
	def __init__(self, stdscr):
		self.stdscr = stdscr
		curses.initscr()
		curses.start_color()
		#curses.use_default_colors()
		#curses.curs_set(0)
		#curses.cbreak()
		curses.halfdelay(10) #nocbreak to cancel
		curses.init_pair(1, 0, curses.COLOR_GREEN)
		curses.init_pair(2, 0, curses.COLOR_BLUE)
		self.log = []
		self.query = ""
		self.initial_time = datetime.datetime.now()
		self.init_windows()

	def get_time(self):
		d = (datetime.datetime.now() - self.initial_time).total_seconds()
		#d = d / 10
		d = d * SPEED_FACTOR
		day = d // (24 * 60)
		d = d % (24 * 60) 
		return "day %d %02d:%02d" % (day + 1, d // 60, d % 60) 

	def add_log(self, text, shift = 0):
		text = "%s: %s" % (self.get_time(), text)
		text = ''.join([' ' for a in range(0, shift)]) + text
		self.log = self.log[-100:]
		self.log.append(text)
		self.add_wrap(self.log_win, text) 

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

	def update_query(self, text):
		self.query = text
		self.query_win.clear()
		self.query_win.addstr(text)
		self.query_win.refresh()
	
	def init_windows(self):
		y, x = self.stdscr.getmaxyx()
		self.query_win = curses.newwin(1, x, y - 2, 0)
		self.log_win = curses.newwin(y - 2, x, 0, 0)
		self.log_win.scrollok(True)
		self.old_y, self.old_x = (y, x)
	
	def resize_windows(self, stdscr):
		y, x = stdscr.getmaxyx()
		if y != self.old_y or x != self.old_x:
			stdscr.clear()
			stdscr.refresh()
			self.old_y = y
			self.old_x = x
			self.query_win.resize(1, x)
			self.query_win.mvwin(y - 2, 0)
			self.log_win.resize(y - 2, x)
			self.log_win.mvwin(0, 0)

			self.log_win.clear()
			for l in self.log:
				self.add_wrap(self.log_win, l)

			self.query_win.clear()
			self.update_query(self.query)

			self.query_win.refresh()
			self.log_win.refresh()


