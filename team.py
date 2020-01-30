import datetime
import copy
import inflect
import math
from tools import *
from command import *
from reply import *
from goal import *

nato = ['alpha', 'bravo', 'charly', 'delta', 'echo', 'fox-trot', 'hotel', 'india', 'juliet', 'kilo', 'lima', 'mike', 'november', 'oscar', 'papa', 'quebec', 'romeo', 'sierra', 'tango', 'uniform', 'victor', 'wiskhey', 'x-ray', 'yankee', 'zulu']

class Team():
	def __init__(self, id_, count, map_, goals, y, x): 
		self.count = count
		self.id = id_
		self.map = map_
		self.other_teams = None 
		self.our_teams = None 
		self.commands = [] # actions to do, [0] is the one being done
		self.nato = nato.pop(0)
		self.letter = self.nato[0]
		self.replies = [] # list of messages returned by the team
		self.npc = False
		self.goals = goals
		self.y = y
		self.x = x
		self.win = False
	
	def get_alive(self):
		return (not self.win) and (self.count > 0)

	def get_pos_from_direction(self, direction):
		y = self.y + (1 if "s" in direction else -1 if "n" in direction else 0)	
		x = self.x + (1 if "e" in direction else -1 if "w" in direction else 0)	
		return y, x 

	def get_item_at_pos(self, direction):
		items = []
		if direction != "l":
			y, x = self.get_pos_from_direction(direction)
			s_direction = direction
		else:
			y = self.y
			x = self.x
			s_direction = "right here"
		if x < 0 or y < 0 or x >= SIZE or y >= SIZE:
			items.append("a border")
		else: 
			if self.map.geo[y][x] == FOREST:
				items.append("a forest")
			if self.map.geo[y][x] == WATER:
				items.append("some water")
			if self.map.geo[y][x] != FOREST: # can't see an ennemy in the forest
				if self.other_teams != None:
					c = 0
					c = sum([a.count for a in self.other_teams.list if a.x == x and a.y == y])
					if c > 0:
						if c > 10:
							items.append("lots of soldiers")
						else:
							items.append("some soldiers")
				c = sum([a.count for a in self.our_teams.list if a.x == x and a.y == y and a.id != self.id and a.get_alive()])
				if c > 0:
					items.append("some fellows")

			if self.map.wonder[y][x] != None:
				items.append(self.map.wonder[y][x])

			for goal in self.goals.list:
				if goal.x == x and goal.y == y:
					items.append("goal %s" % goal.name)
		
		if len(items) == 0:
			txt = None
		else:
			if len(items) > 1:
				s = "%s and %s" % (", ".join(items[0:-1]), items[-1])
			else:
				s = items[0]
			txt = "%s: %s" % (s_direction, s)
		return txt

	def get_ennemies_at_pos(self, direction = "l"): 
		y, x = self.get_pos_from_direction(direction)
		teams = [team for team in self.other_teams.list if team.x == x and team.y == y and team.count > 0]
		return teams
	
	def look(self): 
		items = [] 
		for d in ["l", "n", "ne", "e", "se", "s", "sw", "w", "nw"]:
			item = self.get_item_at_pos(d)
			if item != None:
				items.append(item) 
		if len(items) == 0:
			items.append("nothing")
		return '. '.join(items)

	def move(self, direction):
		y = self.y + (1 if "s" in direction else -1 if "n" in direction else 0)	
		x = self.x + (1 if "e" in direction else -1 if "w" in direction else 0)	
		if y >= SIZE:
			self.add_reply("we reached a border")
			return False
		if y < 0:
			self.add_reply("we reached a border")
			return False
		if x >= SIZE:
			self.add_reply("we reached a border")
			return False
		if x < 0:
			self.add_reply("we reached a border")
			return False
# if end up on water, then also refuse
		if self.map.geo[y][x] == WATER:
			self.add_reply("we can't go pass that water")
			return False
		self.y = y
		self.x = x
		return True

	def pre_command_process(self):
		if len(self.get_ennemies_at_pos()) > 0: 
			if not self.fighting():
				self.apply(CommandFight())

	def fight(self, command):
		killed = random.randrange(0, int(self.count * 2))
		teams = self.get_ennemies_at_pos()
		#log("%s: we killed %d peoples, we have %d peoples left" % (self.nato, killed, self.count)) 
		actually_killed = 0
		for team in teams:
			if killed == 0:
				break 
			k = min(team.count, killed)
			team.count = team.count - k
			killed = killed - k
			actually_killed = actually_killed + k
		command.killed = command.killed + actually_killed
	
	def fighting(self):
		r = False
		if len(self.commands) > 0:
			r = isinstance(self.commands[0], CommandFight)
		return r

	def get_goal_list(self):
		l = []
		for goal in self.goals.list:
			#if goal.team_letter_ids_required == None or self.letter in goal.team_letter_ids_required:
			l.append(goal)
		s = []
		a = 1
		p = inflect.engine()
		for goal in l:
			number = p.number_to_words(p.ordinal(a))
			dist = round(self.get_distance(goal.y, goal.x))
			angle, s_angle = self.get_direction(goal.y, goal.x)
			s.append("%s goal: %s, direction: %s, distance: %0.0f hours." % (number, goal.name, s_angle, dist))
			a = a + 1
		return " ".join(s)

	def is_here(self, location):
		y, x = location
		return y == self.y and x == self.x 

	def get_direction(self, desty, destx):
		y = self.y
		x = self.x
		angle = math.degrees(math.atan2(desty - y, destx - x))
		sd = ["e", "se", "s", "sw", "w", "nw", "n", "ne"] 
		return angle, sd[round(angle / 45) % 8]

	def get_distance(self, desty, destx):
		y = self.y
		x = self.x
		return math.sqrt(math.pow(abs(desty - y), 2) + math.pow(abs(destx - x), 2))

	def get_goals(self):
		return self.get_goal_list()

	def status(self):
		s = "we have %d people left." % self.count
		s = s + " %s." % ("we are a support team" if self.letter != 'a' else "we are the working team")
		return s 

	def get_non_end_goal_list(self):
		goals = [goal for goal in self.goals.list if not goal.done and not(isinstance(goal, EndGoal))]
		return goals

	def get_goal_at_pos(self):
		goals = [goal for goal in self.goals.list if goal.x == self.x and goal.y == self.y]
		if len(goals) > 0:
			return goals[0]
		else:
			return None
	
	def ask_work(self):
		goal = self.get_goal_at_pos()
		if goal == None:
			self.add_reply('no task to do here')
		else:
			if goal.done:
				self.add_reply('that task is already completed')
			else:
				if isinstance(goal, EndGoal):
					if len(self.get_non_end_goal_list()) > 0:
						self.add_reply('we still have tasks to do')
						return
				self.apply(CommandDoWork(goal))
				
	def do_work(self, command):
		if isinstance(command.goal, EndGoal):
			self.win = True
			self.add_reply("we exited, bye")
		else:
			command.goal.done = True 
			self.add_reply("%s is done" % command.goal.name)

	def tick(self): 
		if self.count <= 0:
			return
		self.pre_command_process() 
	
		if len(self.commands) > 0:
			command = self.commands[0]
			if command.when <= datetime.datetime.now():
				self.commands.pop(0) 
				if isinstance(command, CommandFight):
					self.fight(command)
					if len(self.get_ennemies_at_pos()) == 0:
						command.auto_repeat = False
						self.add_reply("we just had a fight, we killed %d peoples" % (command.killed))
# no need to rewrite the command, bc it pops up as long as there are ennemies anyway
				else: 
					if isinstance(command, CommandLook):
						self.add_reply(self.look())
					elif isinstance(command, CommandStatus): 
						self.add_reply(self.status())
					elif isinstance(command, CommandMove):
						if not self.move(command.direction):
							command.auto_repeat = False
					elif isinstance(command, CommandAskWork):
						self.ask_work()
					elif isinstance(command, CommandDoWork):
						self.do_work(command)
					else:
						raise Exception("instance of %s not handled" % str(command))
				if command.auto_repeat:
					self.apply(command)

	def apply_action(self, command):
# we remove all pending command except looking around
		self.commands = [command for command in self.commands if not(isinstance(command, CommandAction))] 
		if len(self.commands) > 0:
			t = max([command.when for command in self.commands])
		else:
			t = datetime.datetime.now() 
		command.when = t + datetime.timedelta(seconds = command.duration)
		self.commands.append(command)

	def apply_query(self, command):
# we shift what we had
		for a in self.commands:
			a.when = a.when + datetime.timedelta(seconds=command.duration)
# we add the new command
		self.commands.insert(0, command) 
		command.when = datetime.datetime.now() + datetime.timedelta(seconds = command.duration)

	def apply(self, command): 
# if a fight is requested, everythg else is cancel
# if a fight is going on, then we ignore everythg else (included the command to fight)
		if (self.fighting()):
			return
		if (self.win):
			return 
		log(str(command))
		if isinstance(command, CommandFight):
			self.commands = [] 
		if isinstance(command, CommandStop):
			self.commands = [] 
		if isinstance(command, CommandAction): # fight included
			self.apply_action(command)
		if isinstance(command, CommandQuery):
			self.apply_query(command)

	def add_reply(self, value):
		if not self.npc:
			reply = Reply(value, self.nato)
			self.replies.append(reply)
	
	def dump_replies(self):
		if self.get_alive():
			r = copy.copy(self.replies)
		else: 
			r = []
		self.replies = []
		return r
