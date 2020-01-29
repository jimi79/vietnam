from const import *
import json

class Query():
	def init(self):
		self.pos = {
			'name': 'team', 
			'values': 
				{a.letter: {
					'text': 'Team %s' % a.nato, 'code': a.id
				} for a in self.teams.list
			}
		}
		self.query = [] # current query
		self.end = False

	def __init__(self, teams):
		self.teams = teams
		self.init() 

	def get_text(self):
		txt = [item['text'] for item in self.query]
		return ' '.join(txt)

	def get_help(self): 
		values = self.pos['values']
		lst = ["%s: %s" % (key, values[key]['text']) for key in values.keys()]
		return "\n".join(lst)

	def next_query(self):
		if len(self.query) == 1:
			self.pos = {
				'name': 'action', 
				'values': 
					{
						'l': {'text': 'look', 'code': COMMAND_LOOK},
						't': {'text': 'status', 'code': COMMAND_STATUS},
						's': {'text': 'stop', 'code': COMMAND_STOP},
						'w': {'text': 'work', 'code': COMMAND_WORK},
						'm': {'text': 'move', 'code': COMMAND_MOVE}
					}
				}

		if len(self.query) == 2:
			if self.query[-1]['code'] == COMMAND_LOOK:
				self.end = True
			if self.query[-1]['code'] == COMMAND_STATUS:
				self.end = True
			if self.query[-1]['code'] == COMMAND_STOP:
				self.end = True 
			if self.query[-1]['code'] == COMMAND_WORK:
				self.end = True
			if self.query[-1]['code'] == COMMAND_MOVE:
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

	def test_key(self, key): 
		if not self.end:
			if key in self.pos['values'].keys():
				self.query.append(
					{
						'code': self.pos['values'][key]['code'],
						'text': self.pos['values'][key]['text']
					})
				self.next_query()
				if self.end:
					return QUERY_DONE
				else:
					return QUERY_NEXT
			else:
				return QUERY_ERR
		else:
			return QUERY_ERR
