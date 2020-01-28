import datetime
import copy
from tools import *
from command import *

nato = ['alpha', 'bravo', 'charly', 'delta', 'echo', 'fox-trot', 'hotel', 'india', 'juliet', 'kilo', 'lima', 'mike', 'november', 'oscar', 'papa', 'quebec', 'romeo', 'sierra', 'tango', 'uniform', 'victor', 'wiskhey', 'x-ray', 'yankee', 'zulu']

class Team():
	def __init__(self, id_, count, map_): 
		self.count = count
		self.id = id_
		self.map = map_
		self.other_teams = None 
		self.our_teams = None 
		self.actions = [] # actions to do, [0] is the one being done
		self.nato = nato[id_]
		self.letter = nato[id_][0]
		self.replies = [] # list of messages returned by the team
		while True:
			self.y = rnd()
			self.x = rnd() # they are parahuted somewhere. could be defined by mission
			if self.map.geo[self.y][self.x] != WATER:
				break
	
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
				c = sum([a.count for a in self.our_teams.list if a.x == x and a.y == y and a.id != self.id])
				if c > 0:
					items.append("some fellows")

			if self.map.stuff[y][x] != None:
				items.append(self.map.stuff[y][x])
		
		if len(items) == 0:
			txt = None
		else:
			if len(items) > 1:
				s = "%s and %s" % (", ".join(items[0:-1]), items[-1])
			else:
				s = items[0]
			txt = "%s: %s" % (s_direction, s)
		return txt

	def get_ennemies_at_pos(self, direction): 
		x, y = self.get_pos_from_direction(direction)
		teams = [team for team in self.other_teams if team.x == x and team.y == y]
		print(teams) 
	
	def look(self): 
# save the map in some file to check, i doubt the display now
# add some details in that log
# TODO !!!!!!!!!!!
# rules about seeing from a forest or not still yet to work on
# actually wrong: we can see a forest, but an ennemie in a forest, we can't tell

		items = [] 
		for d in ["l", "n", "ne", "e", "se", "s", "sw", "w", "nw"]:
			item = self.get_item_at_pos(d)
			#item2 = self.get_ennemies_at_pos(d) # sum of bad guys
			if item != None:
				items.append(item) 
		if len(items) == 0:
			items.append("nothing")
		return ', '.join(items)

	def move(self, direction):
		y = self.y + (1 if "s" in direction else -1 if "n" in direction else 0)	
		x = self.x + (1 if "e" in direction else -1 if "w" in direction else 0)	
		if y >= SIZE:
			return False
		if y < 0:
			return False
		if x >= SIZE:
			return False
		if x < 0:
			return False
# if end up on water, then also refuse
		self.y = y
		self.x = x
		return True

	def tick(self):
		if len(self.actions) > 0:
			action = self.actions[0]
			if action.when <= datetime.datetime.now():
				self.actions.pop(0) # not if moving... but i should regenerate a new order in that case, or change the time of it
				if isinstance(action, CommandLook):
					self.add_reply(self.look())
				if isinstance(action, CommandMove):
					if not self.move(action.direction):
						self.add_reply("we reached a border")

	def apply(self, action):

#TODO: if fighting, then refuse any action command, and add a message

		if isinstance(action, CommandAction): 
# we remove all pending actions except looking around
			self.actions = [action for action in self.actions if not(isinstance(action, CommandAction))] 
			if len(self.actions) > 0:
				t = max([action.when for action in self.actions])
			else:
				t = datetime.datetime.now() 
			action.when = t + datetime.timedelta(seconds = action.duration)
			self.actions.append(action)
		if isinstance(action, CommandLook):
			if len([action for action in self.actions if (isinstance(action, CommandLook))]) == 0:
# we shift what we had
				for a in self.actions:
					a.when = a.when + datetime.timedelta(seconds=action.duration)
# we add the new action
				self.actions.insert(0, action) 
				action.when = datetime.datetime.now() + datetime.timedelta(seconds = action.duration)

	def add_reply(self, value):
		self.replies.append(value)
	
	def dump_replies(self):
		if self.count > 0:
			r = copy.copy(self.replies)
		else: 
			r = []
		self.replies = []
		return r
