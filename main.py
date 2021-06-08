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
		self.term.update_query('confirm closing (y/n)')
		while True:
			curses.cbreak() #nocbreak to cancel
			a = stdscr.getkey()
			if a == 'y' or a == 'n':
				break
		return a == 'y'

	def init_game(self):
		self.map = Map_()
		self.map.place(count_forest = COUNT_FOREST, count_wonder = COUNT_WONDER, count_water = COUNT_WATER)
		self.goals = Goals(self.map) # a list of places, and place on the map the first one to reach
		self.player_teams = Teams(count = COUNT_PLAYER_TEAMS, map_ = self.map, npc = False, goals = self.goals)
		self.player_teams.append_heli(map_ = self.map, npc = False)
		self.npc_teams = Teams(count = COUNT_NPC_TEAMS, map_ = self.map, npc = True, goals = self.goals)
		self.player_teams.set_other_team(self.npc_teams)
		self.npc_teams.set_other_team(self.player_teams)
		self.timed_fight = TimedFight()

	def init(self, stdscr):
		self.term = Term(stdscr)
		self.log = Log()
		self.init_game()

	def tick(self, stdscr):
		self.timed_fight.check(self.map, self.player_teams, self.npc_teams)

		self.player_teams.tick()
		self.npc_teams.tick()

		for reply in self.get_replies():
			self.term.add_log("%s: %s" % (reply.team, reply.text))
		a = self.get_all_teams_status()

		update_reason = self.log.get_update_reason(self.player_teams, self.goals)
		if update_reason:
			self.log.add_log(self.term.get_time(), self.map, self.player_teams, self.npc_teams, self.goals, update_reason, self.term)

		end = False
		if ALL_ALIVE_TEAMS_EXITED in a:
			self.term.add_log('All alive units are safe. Press a key to exit')
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
		self.term.update_query(query.get_text())

	def get_help(self, query):
		self.term.add_log(', '.join(query.get_help()))

	def log_goals(self):
		if DEBUG:
			for goal in self.goals.list:
				self.term.add_log("%s at (%d, %d), done:%s, duration: %0.0f" % (goal.name, goal.y, goal.x, "True" if goal.done else "False", goal.duration))

	def get_all_teams_status(self):
		return self.player_teams.get_all_teams_status()

	def log_status(self):
		a = self.get_all_teams_status()
		self.term.add_log(", ".join(a))

	def log_locations(self):
		p = "player: %s" % ", ".join(self.player_teams.get_debug_infos())
		n = "npc: %s" % ", ".join(self.npc_teams.get_debug_infos())
		self.term.add_log("%s\n%s" % (p, n))

	def log_tasks(self):
		s = []
		s.append("Player's teams:")
		for team in self.player_teams.list:
			s.append("%s: %s" % (team.nato, team.commands.debug()))
		s.append("NPC's teams:")
		for team in self.npc_teams.list:
			s.append("%s: %s" % (team.nato, team.commands.debug()))
		self.term.add_log("\n".join(s))

	def run(self, stdscr):
		self.init(stdscr)

		query = Query(self.player_teams)
		self.update_query(query)
		k = None

		old_time = datetime.datetime.now()
		while True:
			#self.update_time()

# to avoid tick every time a key is pressed
			time = datetime.datetime.now()
			if (time - old_time).total_seconds() > 1:
				if not self.tick(stdscr):
					break
				old_time = time
			self.term.resize_windows(stdscr)

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
						self.print_map(self.term.log_win)

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
							self.term.add_log('you: %s' % query.get_text(), shift=2)
							query.init()
						self.update_query(query)
