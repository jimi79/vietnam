import copy
from const import *
from goals import *

COLOR_NONE = 0
COLOR_FOREST = 1
COLOR_WATER = 2

class PlacedWonder():
	def __init__(self, wonder, y, x, onWater):
		self.wonder = wonder
		self.y = y
		self.x = x
		self.onWater = onWater

class Wonder():
	def __init__(self, name, maxDistanceVisibility):
		self.name = name
		self.maxDistanceVisibility = maxDistanceVisibility

class Map_():
	def __init__(self):
		self.placeFor = {}
		self.geo = [[None for i in range(0, SIZE)] for y in range(0, SIZE)]
		self.wonder = [[None for i in range(0, SIZE)] for y in range(0, SIZE)]
		self.placeFor['forest'] = self.getAllCells()
		self.placeFor['plain'] = self.getAllCells()
		self.placeFor['water'] = self.getAllWaterCells()
		self.placeFor['wonderOnGround'] = self.getAllCells()
		self.placeFor['wonderOnWater'] = []
		self.placeFor['goal'] = self.getAllCells()
		self.placeFor['player'] =self. getAllCells()
		self.placeFor['npc'] = self.getAllCells()
		self.placed = {}
		self.placed['water'] = []
		self.placed['forest'] = []
		self.placedWonders = [] 

	def getAllCells(self):
		a = []
		for y in range(0, SIZE):
			for x in range(0, SIZE):
				a.append((y, x))
		return a

	def getAllWaterCells(self):
		a = []
		for y in range(0, SIZE, 2):
			b = []
			for x in range(0, SIZE):
				b.append((y, x))
			random.shuffle(b)
			b.pop()
			a = a + b
		return a

	def getColor(self, y, x):
		if self.geo[y][x] == None:
			return COLOR_NONE
		if self.geo[y][x] == FOREST:
			return COLOR_FOREST
		if self.geo[y][x] == WATER:
			return COLOR_WATER

	def updatePlains(self):
		self.placed['plain'] = []
		for y in range(0, SIZE):
			for x in range(0, SIZE):
				if self.geo[y][x] == None:
					round.placed['plain'].append((y, x))


	def placeForest(self, count):
		random.shuffle(self.placeFor['forest'])
		while count > 0 and len(self.placeFor['forest']) > 0:
			y, x = self.placeFor['forest'][0]
			self.geo[y][x] = FOREST
			if (y,x) in self.placeFor['water']:
				self.placeFor['water'].remove((y,x))
			self.placeFor['forest'].remove((y,x))
			self.placeFor['wonderOnGround'].remove((y,x))
			count = count - 1
			self.placed['forest'].append((y, x))

	def placeWater(self, count):
		random.shuffle(self.placeFor['water'])
		while count > 0 and len(self.placeFor['water']) > 0:
			y, x = self.placeFor['water'][0]
			self.geo[y][x] = WATER
			self.placed['water'].append((y, x))
			self.placeFor['water'].remove((y,x))
			self.placeFor['wonderOnGround'].remove((y,x))
			self.placeFor['forest'].remove((y,x))
			self.placeFor['player'].remove((y,x))
			self.placeFor['npc'].remove((y,x))
			self.placeFor['goal'].remove((y,x))
			self.placeFor['wonderOnWater'].append((y, x))
			count  = count - 1

	def placeWonder(self, count):
		wonderOnWater = []
		wonderOnWater.append(Wonder("Con Dao Islands", 20))
		wonderOnWater.append(Wonder("Tam Coc", 0))
		wonderOnWater.append(Wonder("My Khe Beach)", 10))
		wonderOnWater.append(Wonder("Cham Islands)", 10))
		wonderOnWater.append(Wonder("Mekong Delta)", 20))
		wonderOnWater.append(Wonder("Phu Quoc", 10))
		wonderOnWater.append(Wonder("Mui Ne", 10))
		wonderOnGround = []
		wonderOnGround.append(Wonder("Khai Dinh Tomb", 0))
		wonderOnGround.append(Wonder("Marble Mountains", 20))
		wonderOnGround.append(Wonder("Hang Son Doong Cave", 0))
		wonderOnGround.append(Wonder("Temple of Literature", 0))
		wonderOnGround.append(Wonder("Bac Ha", 10))
		wonderOnGround.append(Wonder("Hang Nga's Guesthouse", 0))
		wonderOnGround.append(Wonder("Cao Dai Temple", 0))
		wonderOnGround.append(Wonder("Imperial Citadel", 10))
		wonderOnGround.append(Wonder("Sa Pa Terraces", 25))
		wonderOnGround.append(Wonder("Thien Mu Pagoda", 15))
		wonderOnGround.append(Wonder("Yen Tu Mountain", 30))
		wonderOnGround.append(Wonder("Phu Si Lung", 30))
		wonderOnGround.append(Wonder("Fansipan", 60))
		random.shuffle(wonderOnGround)
		random.shuffle(wonderOnWater)
		random.shuffle(self.placeFor['wonderOnWater'])
		random.shuffle(self.placeFor['wonderOnGround'])
		while True:
			if count == 0:
				break
			waterPossible = True
			groundPossible = True
			if len(wonderOnGround) == 0:
				groundPossible = False
			if len(wonderOnWater) == 0:
				waterPossible = False
			if len(self.placeFor['wonderOnGround']) == 0:
				groundPossible = False
			if len(self.placeFor['wonderOnWater']) == 0:
				waterPossible = False
			if (not waterPossible) and (not groundPossible):
				break
			if not waterPossible:
				onWater = False
			elif not groundPossible:
				onWater = True
			else:
				onWater = random.randrange(0, 4) == 3
			if onWater:
				wonder = wonderOnWater.pop(0)
				y, x = self.placeFor['wonderOnWater'].pop(0)
			else:
				wonder = wonderOnGround.pop(0)
				y, x = self.placeFor['wonderOnGround'].pop(0)
			self.placedWonders.append(PlacedWonder(wonder, y, x, onWater))
			self.wonder[y][x] = wonder.name
			count = count - 1

	def place(self, countWater, countForest, countWonder):
		self.placeWater(countWater)
		self.placeForest(countForest)
		self.placeWonder(countWonder)

	def getGoalLocation(self):
		if len(self.placeFor['goal']) > 0:
			random.shuffle(self.placeFor['goal'])
			return self.placeFor['goal'].pop()
		else:
			return (-1, -1)

	def getTeamPlayerLocation(self):
		random.shuffle(self.placeFor['player'])
		return self.placeFor['player'][0]

	def getTeamNpcLocation(self):
		random.shuffle(self.placeFor['npc'])
		return self.placeFor['npc'][0]

	def getTeamNpcPatrolLocation(self, ourY, ourX):
		return [(y, x) for (y, x) in self.placeFor['npc'] if (x != ourX or y != ourY) and ((abs(x - ourX) <= 1) and (abs(y - ourY) <= 1))]


