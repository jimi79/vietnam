import json
from const import *
from team import *

class Query():
	def init(self):
		self.query = [] # current query
		self.end = False
		self.nextQuery()

	def __init__(self, teams):
		self.teams = teams
		self.init() 

	def getText(self):
		txts = []
		for txt in self.query:
			if 'append' in txt.keys():
				txts.append(txt['text'] + txt['append'])
			else:
				txts.append(txt['text'])
		return ' '.join(txts)

	def getHelp(self): 
		values = self.pos['values']
		lst = ["%s: %s" % (key, values[key]['text']) for key in values.keys()]
		return lst

	def nextQuery(self):
		if len(self.query) == 0:
			self.pos = {
				'name': 'team', 
				'values': 
					{
						a.letter:
						{
							'text': 'team %s' % a.nato,
							'code': a.id,
							'append': ','
						} for a in self.teams.list
					}
				}

		if len(self.query) == 1:
			team = self.teams.getTeamByLetter(self.query[0]['code'])
			if isinstance(team, TeamInfantry): # will be TeamInfantry
				self.pos = {
					'name': 'action', 
					'values': 
					{
						'l': {'text': 'look', 'code': COMMAND_LOOK},
						't': {'text': 'status', 'code': COMMAND_STATUS},
						's': {'text': 'stop', 'code': COMMAND_STOP},
						'w': {'text': 'work', 'code': COMMAND_WORK},
						'M': {'text': 'start moving', 'code': COMMAND_MOVE},
						'm': {'text': 'move for %0.0f km' % CELL_RESOLUTION, 'code': COMMAND_MOVE_ONCE}
					}
				}
			elif isinstance(team, TeamHelicopter): # will be TeamInfantry
				self.pos = {
					'name': 'action', 
					'values': 
					{
						'd': {'text': 'get directions', 'code': COMMAND_GET_DIRECTIONS},
					}
				} 

		if len(self.query) == 2:
			if self.query[-1]['code'] == COMMAND_LOOK:
				self.end = True
			if self.query[-1]['code'] == COMMAND_GET_DIRECTIONS:
				self.end = True
			if self.query[-1]['code'] == COMMAND_STATUS:
				self.end = True
			if self.query[-1]['code'] == COMMAND_STOP:
				self.end = True 
			if self.query[-1]['code'] == COMMAND_WORK:
				self.end = True
			if self.query[-1]['code'] == COMMAND_MOVE or self.query[-1]['code'] == COMMAND_MOVE_ONCE:
				self.pos = {
					'name': 'direction', 
					'values': 
						{
							'w': {'text': 'north', 'code': 'n'},
							'e': {'text': 'north east', 'code': 'ne'},
							'd': {'text': 'east', 'code': 'e'},
							'c': {'text': 'south east', 'code': 'se'},
							'x': {'text': 'south', 'code': 's'},
							'z': {'text': 'south west', 'code': 'sw'},
							'a': {'text': 'west', 'code': 'w'},
							'q': {'text': 'north west', 'code': 'nw'}
						}
					}
		if len(self.query) == 3:
			self.end = True

	def testKey(self, key): 
		if not self.end:
			if key in self.pos['values'].keys():
				self.query.append( self.pos['values'][key])
				self.nextQuery()
				if self.end:
					return QUERY_DONE
				else:
					return QUERY_NEXT
			else:
				return QUERY_ERR
		else:
			return QUERY_ERR

	def deleteLast(self):
		if len(self.query) > 0:
			self.query = self.query[0:-1]
			self.nextQuery()

	def getTeam(self): 
		team = None
		if len(self.query) > 0:	
			team = self.teams.getTeamByLetter(self.query[0]['code'])
		return team

