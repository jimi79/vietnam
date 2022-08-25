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

	def addWrap(self, text):
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
			self.addWrap(l) 

	def addText(self, text): 
		#self.log = self.log[-100:]
		self.log.append(text)
		self.addWrap(text)

class WindowHandler():
	def __init__(self, stdscr, teams):
		self.teamWindows = []
		self.stdscr = stdscr
		self.teams = teams
		self.oldX = 0
		self.oldY = 0
		self.query = ""
		self.init()

	def init(self):
		index = 0
		y, x = self.stdscr.getmaxyx() 
		for team in self.teams.list:
			window = Window(index, TEAM_WINDOW, curses.newwin(1, x, index, 0))
			index = index + 1 
			self.teamWindows.append(window)
			team.window = window
		window = curses.newwin(1, x, index, 0)
		self.queryWin = Window(index, PLAYER_WINDOW, window)
		self.layout = HORZ
		self.resize()

	def resize(self):
		y, x = self.stdscr.getmaxyx() 
		if (y != self.oldY) or (x != self.oldX):
			self.stdscr.clear()
			self.stdscr.refresh()
			self.oldX = x
			self.oldY = y
			if self.layout == HORZ:
				self.queryWin.window.resize(2, x)
				self.queryWin.window.mvwin(y - 2, 0)
				y = y - 1 # what's left of the screen
				heightPerWin = int(y / 4)
				top = 0
				for window in self.teamWindows:
					window.window.resize(heightPerWin, x)
					window.window.mvwin(window.index * heightPerWin, 0) 
					window.refill() 
			else:
				raise Exception("not handled")
			self.updateQuery(self.query)
	
	def addText(self, window, text):
		window.addText(text)

	def updateQuery(self, text):
		self.query = ""
		self.queryWin.window.clear()
		self.queryWin.window.addstr(text)
		self.queryWin.window.refresh() 
		self.queryWin.window.addstr("test")

class Term():
	def __init__(self, stdscr, teams):
		self.stdscr = stdscr
		curses.initscr()
		curses.start_color()
		#curses.useDefaultColors()
		#curses.cursSet(0)
		#curses.cbreak()
		curses.halfdelay(10) #nocbreak to cancel
		curses.init_pair(1, 0, curses.COLOR_GREEN)
		curses.init_pair(2, 0, curses.COLOR_BLUE)
		self.initialTime = datetime.datetime.now()
		self.handler = WindowHandler(stdscr, teams)

	def getTime(self):
		d = (datetime.datetime.now() - self.initialTime).total_seconds()
		#d = d / 10
		d = d * SPEED_FACTOR
		day = d // (24 * 60)
		d = d % (24 * 60) 
		return "day %d %02d:%02d" % (day + 1, d // 60, d % 60) 

	def addLog(self, text, shift = 0, team = None):
		text = "%s: %s" % (self.getTime(), text)
		text = ''.join([' ' for a in range(0, shift)]) + text
		if team is None:
			for win in self.handler.teamWindows:
				self.handler.addText(win, text)
		else:
			self.handler.addText(team.window, text)

	def updateQuery(self, text):
		self.handler.updateQuery(text)

	def resize(self):
		self.handler.resize()
