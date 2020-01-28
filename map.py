import copy
from const import *
from goals import *


stuff_on_plain = ["Khai Dinh Tomb", "a village", "Marble Mountains", "Hang Son Doong Cave", "Temple of Literature", "Bac Ha", "Hang Nga's Guesthouse", "Cao Dai Temple", "Imperial Citadel", "Mui Ne", "Sa Pa Terraces", "Thien Mu Pagoda"]
stuff_on_water = ["Con Dao Islands", "Tam Coc", "My Khe Beach", "Cham Islands", "Mekong Delta", "Phu Quoc"]

class Map_():
	def __init__(self):
		self.geo = [[None for i in range(0, SIZE)] for j in range(0, SIZE)]
		self.stuff = [[None for i in range(0, SIZE)] for j in range(0, SIZE)]
		self.goals = Goals()
		self.forest_cells = []
		self.plain_cells = []
		self.water_cells = []

	def get_color(self, y, x):
		if self.geo[y][x] == None:
			return COLOR_NONE
		if self.geo[y][x] == FOREST:
			return COLOR_FOREST
		if self.geo[y][x] == WATER:
			return COLOR_WATER

	def randomize(self):
		for i in range(0, 12):
			x = rnd()
			y = rnd()
			self.geo[y][x] = FOREST
		for i in range(0, 7):
			x = rnd()
			y = rnd()
			self.geo[y][x] = WATER
		self.init_list_geo()
		self.add_stuff(int(SIZE * SIZE * 0.1)) # 10% of the surface

	def init_list_geo(self):
		for y in range(0, SIZE):
			for x in range(0, SIZE):
				if self.geo[y][x] == WATER:
					self.water_cells.append((y, x))
				else:
					if self.geo[y][x] == FOREST:
						self.forest_cells.append((y, x)) 
					else:
						self.plain_cells.append((y, x))


	def add_stuff_stuff(self, stuff, cells):
		y, x = cells.pop(0)
		item = stuff.pop(0)
		self.stuff[y][x] = item
		print(item)
	
	def add_stuff(self, count):
		s_water = copy.copy(stuff_on_water)
		s_plain = copy.copy(stuff_on_plain)
		c_water = copy.copy(self.water_cells)
		c_plain = copy.copy(self.plain_cells)
		c_forest = copy.copy(self.forest_cells)
		random.shuffle(s_water)
		random.shuffle(s_plain)
		random.shuffle(c_water)
		random.shuffle(c_plain)
		random.shuffle(c_forest)
		for i in range(0, int(count * 1/3)):
			if len(s_water) == 0 or len(c_water) == 0:
				break
			self.add_stuff_stuff(s_water, c_water)
		for i in range(0, int(count * 2/3)):
			if len(s_plain) == 0 or len(c_plain) == 0:
				break
			self.add_stuff_stuff(s_plain, c_plain)
