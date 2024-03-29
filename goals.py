from goal import *

randomGoals = [
	MiddleGoal('build a bridge for our vehicles', 4 * 60),
	MiddleGoal('destroy an ammunation depot', 1 * 60),
	MiddleGoal('massacre a village', 3 * 60),
	MiddleGoal('reckon and find a target to spread agent orange', 1 * 60),
	MiddleGoal('torture villager to get vietcongs whereabouts', 2 * 60),
	MiddleGoal('reckon and find a target to drop napalm', 1 * 60),
	]

randomEndGoals = [
	EndGoal('exit point', 30)
]

class Goals():
	def __init__(self, map_):
		self.list = []
		self.map = map_
		for i in range(0, GOAL_COUNT):
			self.addRandomGoal(randomGoals)
		self.addRandomGoal(randomEndGoals)

	def addRandomGoal(self, list_):
		random.shuffle(list_)
		y, x = self.map.getGoalLocation()
		if y != -1:
			if len(randomGoals) > 0:
				goal = list_.pop()
				goal.y = y
				goal.x = x
				self.list.append(goal)

	def getPendingList(self):
		return [g for g in self.list if not g.done]
