import copy
from const import *
from goals import *


class Map_():


	def get_all_cells(self):
		a = []
		for y in range(0, SIZE):
			for x in range(0, SIZE):
				a.append((y, x))
		return a

	def get_all_water_cells(self):
		a = []
		for y in range(0, SIZE, 2):
			b = []
			for x in range(0, SIZE):
				b.append((y, x))
			random.shuffle(b)
			b.pop()
			a = a + b
		return a
		
	def __init__(self): 
		self.place_for = {}
		self.geo = [[None for i in range(0, SIZE)] for y in range(0, SIZE)]
		self.wonder = [[None for i in range(0, SIZE)] for y in range(0, SIZE)]
		self.place_for['forest'] = self.get_all_cells()
		self.place_for['plain'] = self.get_all_cells()
		self.place_for['water'] = self.get_all_water_cells()
		self.place_for['wonder_on_ground'] = self.get_all_cells()
		self.place_for['wonder_on_water'] = []
		self.place_for['goal'] = self.get_all_cells()
		self.place_for['player'] =self. get_all_cells()
		self.place_for['npc'] = self.get_all_cells()
		self.placed = {}
		self.placed['water'] = []
		self.placed['forest'] = []

	def get_color(self, y, x):
		if self.geo[y][x] == None:
			return COLOR_NONE
		if self.geo[y][x] == FOREST:
			return COLOR_FOREST
		if self.geo[y][x] == WATER:
			return COLOR_WATER

	def update_plains(self):
		self.placed['plain'] = []
		for y in range(0, SIZE):
			for x in range(0, SIZE):
				if self.geo[y][x] == None:
					self.placed['plain'].append((y, x))


	def place_forest(self, ratio):
		count = int(SIZE * SIZE * ratio)
		random.shuffle(self.place_for['forest'])
		while count > 0 and len(self.place_for['forest']) > 0:
			y, x = self.place_for['forest'][0]
			self.geo[y][x] = FOREST
			if (y,x) in self.place_for['water']:
				self.place_for['water'].remove((y,x))
			self.place_for['forest'].remove((y,x))
			self.place_for['wonder_on_ground'].remove((y,x))
			count = count - 1
			self.placed['forest'].append((y, x)) 
			print("placing forest on %d %d" % (y, x))

	def place_water(self, ratio): 
		count = int(SIZE * SIZE * ratio)
		random.shuffle(self.place_for['water'])
		while count > 0 and len(self.place_for['water']) > 0:
			y, x = self.place_for['water'][0]
			self.geo[y][x] = WATER
			self.placed['water'].append((y, x))
			self.place_for['water'].remove((y,x))
			self.place_for['wonder_on_ground'].remove((y,x))
			self.place_for['forest'].remove((y,x))
			self.place_for['player'].remove((y,x))
			self.place_for['npc'].remove((y,x))
			self.place_for['goal'].remove((y,x))
			self.place_for['wonder_on_water'].append((y, x))
			count  = count - 1
			print("placing water on %d %d" % (y, x))

	def place_wonder(self, ratio): 
		wonder_on_water = ["Con Dao Islands", "Tam Coc", "My Khe Beach", "Cham Islands", "Mekong Delta", "Phu Quoc"]
		wonder_on_ground = ["Khai Dinh Tomb", "a village", "Marble Mountains", "Hang Son Doong Cave", "Temple of Literature", "Bac Ha", "Hang Nga's Guesthouse", "Cao Dai Temple", "Imperial Citadel", "Mui Ne", "Sa Pa Terraces", "Thien Mu Pagoda"]
		random.shuffle(wonder_on_ground)
		random.shuffle(wonder_on_water)
		random.shuffle(self.place_for['wonder_on_water'])
		random.shuffle(self.place_for['wonder_on_ground'])
		count = int(SIZE * SIZE * ratio)
		while True:
			if count == 0:
				break 
			water_possible = True
			ground_possible = True
			if len(wonder_on_ground) == 0:
				ground_possible = False
			if len(wonder_on_water) == 0:
				water_possible = False 
			if len(self.place_for['wonder_on_ground']) == 0:
				ground_possible = False
			if len(self.place_for['wonder_on_water']) == 0:
				water_possible = False 
			if (not water_possible) and (not ground_possible):
				break
			if not water_possible:
				on_water = False
			elif not ground_possible:
				on_water = True
			else:
				on_water = random.randrange(0, 4) == 3 
			if on_water:
				wonder = wonder_on_water.pop(0)
				y, x = self.place_for['wonder_on_water'].pop(0)
			else:
				wonder = wonder_on_ground.pop(0)
				y, x = self.place_for['wonder_on_ground'].pop(0)
			self.wonder[y][x] = wonder
			print("Placing %s on %d %d" % (wonder, y, x))
			count = count - 1 

	def place(self, ratio_water = 0.3, ratio_forest = 0.4, ratio_wonder = 0.3):
		self.place_water(ratio_water)
		self.place_forest(ratio_forest)
		self.place_wonder(ratio_wonder)

	def get_goal_location(self):
		random.shuffle(self.place_for['goal'])
		return self.place_for['goal'].pop()

	def get_team_player_location(self):
		random.shuffle(self.place_for['player'])
		return self.place_for['player'][0]

	def get_team_npc_location(self):
		random.shuffle(self.place_for['npc'])
		return self.place_for['npc'][0] 

	def get_team_npc_patrol_location(self, our_y, our_x):
		return [(y, x) for (y, x) in self.place_for['npc'] if x != our_x and y != our_y and ((abs(x - our_x) <= 1) and (abs(y - our_y) <= 1))]
