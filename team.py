import datetime
import copy
import math
from tools import *
from command import *
from reply import *
from goal import *

class Team():
	def __init__(self, id_, name): 
		self.id = id_
		self.commands = Commands()
		self.nato = name
		self.letter = name[0] 
		self.replies = [] # list of messages returned by the team 
		self.other_teams = None 
		self.our_teams = None 
		self.npc = False
		self.fighting = False

	def get_direction(self, desty, destx):
		y = self.y
		x = self.x
		angle = math.degrees(math.atan2(desty - y, destx - x))
		sd = ["east", "south east", "south", "south west", "west", "north west", "north", "north east"] 
		return angle, sd[round(angle / 45) % 8]

	def get_distance(self, desty, destx):
		y = self.y
		x = self.x
		return math.sqrt(math.pow(abs(desty - y), 2) + math.pow(abs(destx - x), 2))

	def add_reply(self, value):
		if not self.npc:
			reply = Reply(value, self)
			self.replies.append(reply)
	
	def dump_replies(self):
		if self.get_alive():
			r = copy.copy(self.replies)
		else: 
			r = []
		self.replies = []
		return r
	
class TeamInfantry(Team):
	def __init__(self, id_, count, goals, y, x, name): 
		super().__init__(id_, name = name)
		self.goals = goals
		self.y = y
		self.x = x
		self.exited = False
		self.count = count 
	
	def tick(self): 
# we don't handle fight here, fights are handled by somethg else.
# but still, there is a command added to the list, that will prevent other commands to be added
		if not self.get_exists():
			self.commands.reset()
			return

		if len(self.commands.list) > 0:
			command = self.commands.list[0] 
			if command.when <= datetime.datetime.now():
				self.commands.list.pop(0) 
# no need to rewrite the command, bc it pops up as long as there are ennemies anyway
				if isinstance(command, CommandFight):
					pass
				elif isinstance(command, CommandStop):
					self.commands.reset()
					self.add_reply('we stopped') 
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
			s_direction = direction.upper()
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
						if c < 5:
							r = 5
						else:
							r = round(c / 5, 0) * 5
						items.append("around %d soldiers" % (r))
				for team in [a for a in self.our_teams.get_infrantry_list() if a.x == x and a.y == y and a.id != self.id and a.get_exists()]:
					items.append("team %s" % team.nato)
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
			items.append("nothing around us")
		return 'we see: %s.' % ('. '.join(items))

	def do_move(self, command):
		direction = command.direction
		y = self.y + (1 if "s" in direction else -1 if "n" in direction else 0)	
		x = self.x + (1 if "e" in direction else -1 if "w" in direction else 0)	
		stop = False
		if y >= SIZE:
			self.add_reply("we reached a border.")
			stop = True
		elif y < 0:
			self.add_reply("we reached a border.")
			stop = True
		elif x >= SIZE:
			self.add_reply("we reached a border.")
			stop = True
		elif x < 0:
			self.add_reply("we reached a border.")
			stop = True
# if end up on water, then also refuse
		elif self.map.geo[y][x] == WATER:
			self.add_reply("we can't go pass that water.")
			stop = True
		elif isinstance(command, CommandMoveOnce):
			self.add_reply("we are at the new location.")
			self.commands.add(CommandLook())
		if stop:
			self.commands.add(CommandLook())
		else:
			self.y = y
			self.x = x
		return not stop

	def fighting(self):
		r = [c for c in self.commands.list if isinstance(c, CommandFight)]
		r = len(r) > 0
		return r

	def get_goal_list(self):
		l = []
		for goal in self.goals.list:
			l.append(goal)
		s = []
		number = 1
		for goal in l:
			dist = round(self.get_distance(goal.y, goal.x))
			angle, s_angle = self.get_direction(goal.y, goal.x)
			s.append("goal %d: %s, direction: %s, distance: %0.0f hours." % (number, goal.name, s_angle, dist))
			number = number + 1
		return " ".join(s)

	def is_here(self, location):
		y, x = location
		return y == self.y and x == self.x 

	def status(self):
		s = ["we are %d people." % self.count]
		if len(self.commands.list) > 0: 
			if isinstance(self.commands.list[0], CommandLook):
				s.append('we are looking around.')

			elif isinstance(self.commands.list[0], CommandMove) or isinstance(self.commands.list[0], CommandMoveOnce):
				s.append('we are moving.')
			elif isinstance(self.commands.list[0], CommandDoWork):
				if isinstance(self.commands.list[0].goal, EndGoal):	
					s.append('we are evacuating.')
				else:
					s.append('we are working.')
		return ' '.join(s)

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

	def do_work(self, command):
		if isinstance(command.goal, EndGoal):
			self.exited = True
			self.add_reply("we exited, bye")
		else:
			if command.goal.done:
				self.add_reply("%s was done by someone else." % command.goal.name)
			else:
				command.goal.done = True 
				self.add_reply("%s is done." % command.goal.name)

	def do_patrol(self, command):
		if self.x == command.x and self.y == command.y:
			random.shuffle(command.locations)
			self.y = command.locations[0][0]
			self.x = command.locations[0][1]
		else:
			self.x = command.x
			self.y = command.y

	def do_ask_work(self):
		works = [g for g in self.goals.list if g.x == self.x and g.y == self.y]
		if len(works) == 0:
			self.add_reply('there is nothing to do here.')
		else:
			work = works[0] # work at that pos
			doit = True
			if isinstance(work, EndGoal):
				works = [g for g in self.goals.list if (not isinstance(g, EndGoal)) and (not g.done)] # work left to be done
				if len(works) > 0:
					self.add_reply("We can't evacuate right now, there are things to do.")
					doit = False
			else: 
				if work.done:
					self.add_reply('this task is already done.')
					doit = False
			if doit:
				self.commands.add(CommandDoWork(work)) 

class TeamHelicopter(Team):
	def __init__(self, id_, name):
		super().__init__(id_ = id_, name = name)
		self.exited = False
	
	def tick(self): 
		if len(self.commands.list) > 0:
			command = self.commands.list[0]
			if command.when <= datetime.datetime.now():
				self.commands.list.pop(0)
				if isinstance(command, CommandAskGetDirections):
					if len(self.commands.list) == 0:
						self.add_reply('we are taking off.')
						self.commands.add(CommandDoGetDirections())
					else:
						if (isinstance(self.commands.list[0], CommandDoGetDirections)):
							self.add_reply("we are already on a reckon mission.")
						elif (isinstance(self.commands.list[0], CommandGoingBackToBase)):
							self.add_reply("we can't doing reckon now, not enough fuel.")
						elif (isinstance(self.commands.list[0], CommandRefuelling)):
							self.add_reply("we are busy refuelling.") 
						else:
							raise Exception("we have a %s" % str(self.commands.list[0]))
				elif isinstance(command, CommandDoGetDirections):
					self.do_get_directions()
				elif isinstance(command, CommandGoingBackToBase):
					self.going_back_to_base()
				elif isinstance(command, CommandRefuelling):
					self.add_reply("refuelling done.") 
	
	def get_alive(self):
		return True
	
	def fighting(self):
		return False
	
	def round_distance(self, value):
		approxs = [1,2,5,8,10,15,20,30,40,50,60,70,100,150,200,300,400,500]
		dists = [(a, abs(a - value)) for a in approxs]
		dists.sort(key = lambda x:abs(x[1]))
		return dists[0][0]

	def do_get_directions(self):
		s = []
		l = [t for t in self.our_teams.list if isinstance(t, TeamInfantry)]
		for team in l:
			if team.get_exists():
				gl = team.goals.get_pending_list()
				if len(gl) > 0:
					s2 = []
					for g in gl:
						dist = self.round_distance(team.get_distance(g.y, g.x) * CELL_RESOLUTION)
						dir_ = team.get_direction(g.y, g.x)
						goal_name = 'exit point' if isinstance(g, EndGoal) else 'the "%s" task' % g.name
						if dist < CELL_RESOLUTION:
							s2.append("close to %s" % (goal_name))
						else:
							s2.append("at %0.0f km %s of %s" % (dist, dir_[1], goal_name))
					s.append("team %s is %s." % (team.nato, ', '.join(s2)))
				else:
					s.append("team %s has nothing to do." % team.nato)
			else:
				s.append("team %s was not spotted." % team.nato)
		s.append("we're going back to the base.")
		for a in s:
			self.add_reply(a)
		self.commands.add(CommandGoingBackToBase()) 

	def going_back_to_base(self): 
		self.add_reply("we are back to the base, refuelling now.")
		self.commands.add(CommandRefuelling()) 

