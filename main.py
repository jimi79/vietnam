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
from term import *
from log import *

class Main(): 
	def confirm(self, stdscr):
		self.term.updateQuery('confirm closing (y/n)')
		while True:
			curses.cbreak() #nocbreak to cancel
			a = stdscr.getkey()
			if a == 'y' or a == 'n':
				break
		return a == 'y'

	def initGame(self):
		self.map = Map_()
		self.map.place(countForest = COUNT_FOREST, countWonder = COUNT_WONDER, countWater = COUNT_WATER)
		self.goals = Goals(self.map) # a list of places, and place on the map the first one to reach
		self.playerTeams = Teams(count = COUNT_PLAYER_TEAMS, map_ = self.map, npc = False, goals = self.goals)
		self.playerTeams.appendHeli(map_ = self.map, npc = False)
		self.npcTeams = Teams(count = COUNT_NPC_TEAMS, map_ = self.map, npc = True, goals = self.goals)
		self.playerTeams.setOtherTeam(self.npcTeams)
		self.npcTeams.setOtherTeam(self.playerTeams)
		self.timedFight = TimedFight()

	def init(self, stdscr):
		self.log = Log()
		self.initGame() 
		self.term = Term(stdscr, self.playerTeams)

	def tick(self, stdscr):
		self.timedFight.check(self.map, self.playerTeams, self.npcTeams)

		self.playerTeams.tick()
		self.npcTeams.tick()

		for reply in self.getReplies():
			self.term.addLog("%s: %s" % (reply.team.nato, reply.text), 0, reply.team)
		a = self.getAllTeamsStatus()

		updateReason = self.log.getUpdateReason(self.playerTeams, self.goals)
		if updateReason:
			self.log.addLog(self.term.getTime(), self.map, self.playerTeams, self.npcTeams, self.map.placedWonders, self.goals, updateReason, self.term)

		end = False
		if ALL_ALIVE_TEAMS_EXITED in a:
			self.term.addLog('All alive units are safe. Press a key to exit')
			end = True

		if end:
			curses.cbreak() #nocbreak to cancel
			a = stdscr.getch() # no halfkey here
			return False
		return True

	def printMap(self, win):
		win.clear()
		for y in range(0, SIZE):
			for x in range(0, SIZE):
				c = self.map.getColor(y, x)
				ch = ' '
				if self.npcTeams.getChar(y, x):
					ch = 'N'
				if self.playerTeams.getChar(y, x):
					ch = 'P'
				win.addstr(ch, curses.colorPair(c))
			win.addstr("\n")
		win.refresh()

	def getKey(self, stdscr):
		curses.halfdelay(10) #nocbreak to cancel
		key = stdscr.getch()
		if key == -1:
			return None
		return key

	def getReplies(self):
		return self.playerTeams.getReplies()

	def updateQuery(self, query):
		self.term.updateQuery(query.getText())

	def getHelp(self, query):
		self.term.updateQuery(', '.join(query.getHelp()))

	def logGoals(self):
		if DEBUG:
			for goal in self.goals.list:
				self.term.addLog("%s at (%d, %d), done:%s, duration: %0.0f" % (goal.name, goal.y, goal.x, "True" if goal.done else "False", goal.duration))

	def getAllTeamsStatus(self):
		return self.playerTeams.getAllTeamsStatus()

	def logStatus(self):
		a = self.getAllTeamsStatus()
		self.term.addLog(", ".join(a))

	def logLocations(self):
		p = "player: %s" % ", ".join(self.playerTeams.getDebugInfos())
		n = "npc: %s" % ", ".join(self.npcTeams.getDebugInfos())
		self.term.addLog("%s\n%s" % (p, n))

	def logTasks(self):
		s = []
		s.append("Player's teams:")
		for team in self.playerTeams.list:
			s.append("%s: %s" % (team.nato, team.commands.debug()))
		s.append("NPC's teams:")
		for team in self.npcTeams.list:
			s.append("%s: %s" % (team.nato, team.commands.debug()))
		self.term.addLog("\n".join(s))

	def run(self, stdscr):
		self.init(stdscr)

		query = Query(self.playerTeams)
		self.updateQuery(query)
		k = None

		oldTime = datetime.datetime.now()
		while True:
			#self.updateTime()

# to avoid tick every time a key is pressed
			time = datetime.datetime.now()
			if (time - oldTime).total_seconds() > 1:
				if not self.tick(stdscr):
					break
				oldTime = time
			self.term.resize()

			k = self.getKey(stdscr)
			if k != None:
				if DEBUG:
					if k == ord('1'):
						self.logGoals()
					elif k == ord('2'):
						self.logStatus()
					elif k == ord('3'):
						self.logLocations()
					elif k == ord('4'):
						self.logTasks()
					elif k == ord('5'):
						self.printMap(self.term.logWin)

				if k == ord('Q'):
					if self.confirm(stdscr):
						break
					else:
						self.updateQuery(query)
				elif k == ord('\t'):
					self.getHelp(query)
				elif k == curses.KEY_BACKSPACE:
					query.deleteLast()
					self.updateQuery(query)
				elif k == 27:
					query.init()
					self.updateQuery(query)
				else:
					k = chr(k)
					state = query.testKey(k)
					if state != QUERY_ERR:
						if state == QUERY_DONE:
							self.playerTeams.apply(query)
							self.term.addLog('you: %s' % query.getText(), 2, query.getTeam()) # TODO no idea how to identify the team concerned, check query
							query.init()
						self.updateQuery(query)
