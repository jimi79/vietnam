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
	def __init__(self, id_, map_): 
		self.id = id_
		self.map = map_
		self.commands = Commands()
		self.nato = nato.pop(0)
		self.letter = self.nato[0]

		self.replies = [] # list of messages returned by the team

		self.other_teams = None 
		self.our_teams = None 
		self.npc = False

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
	
class TeamInfantry(Team):
	def __init__(self, id_, count, map_, goals, y, x): 
		super().__init__(id_, map_)
		self.goals = goals
		self.y = y
		self.x = x
		self.exited = False
		self.count = count 
	
	def tick(self): 
		if not self.get_exists():
			self.commands.reset()
			return
		self.handle_external_events() 
	
		if len(self.commands.list) > 0:
			command = self.commands.list[0]
			if command.when <= datetime.datetime.now():
				self.commands.list.pop(0) 
				if isinstance(command, CommandFight):
					self.fight(command)
					if len(self.get_ennemies_at_pos()) == 0:
						command.auto_repeat = False
						self.add_reply("we just had a fight, we killed %d peoples" % (command.killed))
# no need to rewrite the command, bc it pops up as long as there are ennemies anyway
				elif isinstance(command, CommandLook):
					self.do_look()
				elif isinstance(command, CommandStatus): 
					self.add_reply(self.status())
				elif isinstance(command, CommandMove) or isinstance(command, CommandMoveOnce):
					if not self.do_move(command):
						command.auto_repeat = False
				elif isinstance(command, CommandPatrol):
					self.do_patrol(command)
				elif isinstance(command, CommandAskWork):
					self.do_ask_work()
				elif isinstance(command, CommandDoWork):
					self.do_work(command)
				else:
					raise Exception("instance of %s not handled" % str(command))
				if command.auto_repeat:
					self.commands.add(command)

	def get_alive(self):
		return (self.count > 0)
	
	def get_exists(self):
		return (not self.exited) and (self.count > 0)

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
			s_direction = "here"
		if x < 0 or y < 0 or x >= SIZE or y >= SIZE:
			items.append("a border")
		else: 
			if self.map.geo[y][x] == FOREST:
				items.append("a forest")
			if self.map.wonder[y][x] != None:
				items.append(self.map.wonder[y][x])
			else:
				if self.map.geo[y][x] == WATER:
					items.append("some water")  # if there is a wonder, no need to mention the water, it's obvious

			if self.map.geo[y][x] != FOREST: # can't see an ennemy in the forest
				if self.other_teams != None:
					c = 0
					c = sum([a.count for a in self.other_teams.get_infrantry_list() if a.x == x and a.y == y])
					if c > 0:
						if c > 10:
							items.append("lots of soldiers")
						else:
							items.append("some soldiers")
				c = sum([a.count for a in self.our_teams.get_infrantry_list() if a.x == x and a.y == y and a.id != self.id and a.get_exists()])
				if c > 0:
					items.append("some fellows")


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
		teams = [team for team in self.other_teams.get_infrantry_list() if team.x == x and team.y == y and team.count > 0]
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

	def do_move(self, command):
		direction = command.direction
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
		else:
			if isinstance(command, CommandMoveOnce):
				self.add_reply("we are at the new location")
		self.y = y
		self.x = x
		return True

	def handle_external_events(self):
		if len(self.get_ennemies_at_pos()) > 0: 
			if not self.fighting():
				self.commands.add(CommandFight())

	def fight(self, command):
		killed = random.randrange(0, int(self.count * 2))
		teams = self.get_ennemies_at_pos()
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
		r = [c for c in self.commands.list if isinstance(c, CommandFight)]
		r = len(r) > 0
		return r

	def get_goal_list(self):
		l = []
		for goal in self.goals.list:
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

	def status(self):
		s = "we have %d people left." % self.count
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
	

	def do_look(self):
		self.add_reply(self.look())

	def do_fight(self):
		pass

	def do_work(self, command):
		if isinstance(command.goal, EndGoal):
			self.exited = True
			self.add_reply("we exited, bye")
		else:
			if command.goal.done:
				self.add_reply("%s was done by someone else" % command.goal.name)
			else:
				command.goal.done = True 
				self.add_reply("%s is done" % command.goal.name)

	def do_patrol(self, command):
		if self.x == command.x and self.y == command.y:
			random.shuffle(command.locations)
			self.y = command.locations[0][0]
			self.x = command.locations[0][1]
		else:
			self.x = command.x
			self.y = command.y


	def do_ask_work(self):
		work = [g for g in self.goals.list if g.x == self.x and g.y == self.y]
		if len(work) == 0:
			self.add_reply('there is nothing to do here')
		else:
			self.commands.add(CommandDoWork(work[0]))

class TeamHelicopter(Team):
#TODO in progress (nothing works for now)
	def __init__(self, id_, map_):
		super().__init__(id_, map_)
		self.exited = False
	
	def tick(self): 
		if len(self.commands.list) > 0:
			command = self.commands.list[0]
			if command.when <= datetime.datetime.now():
				self.commands.pop(0)
				if isinstance(command, CommandAskGetDirections):
					if len(self.commands[1:]) == 0:
						self.request(CommandDoGetDirections())
					else:
						if (isinstance(self.commands[0], CommandDoGetDirections)):
							self.add_reply("we are already on a reckon mission")
						if (isinstance(self.commands[0], CommandRefuelling)):
							self.add_reply("we are refuelling") 
				elif isinstance(command, CommandDoGetDirections):
					self.do_get_directions()
				elif isinstance(command, CommandRefuelling):
					self.add_reply("refuelling done") 
	
	def get_alive(self):
		return True
	
	def fighting(self):
		return False
	
	def do_get_directions(self):
		self.add_reply("Here are the directions")
		self.request(CommandRefuelling())

		
