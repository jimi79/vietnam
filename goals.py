from goal import *

random_goals = [
	MiddleGoal('build a bridge for our vehicles', 4 * 60),
	MiddleGoal('destroy an ammunation depot', 1 * 60),
	MiddleGoal('give weapons to a local population', 2 * 60),
	MiddleGoal('massacre a village', 2 * 60),
	MiddleGoal('reckon the best place to spread agent orange', 2 * 60),
	MiddleGoal('torture innocents', 2 * 60),
	]

random_end_goals = [
	EndGoal('exit point', 30)
]

class Goals(): 
	def add_random_goal(self, list_):
		random.shuffle(list_)
		y, x = self.map.get_goal_location()
		if y != -1:
			if len(random_goals) > 0:
				goal = list_.pop()
				goal.y = y
				goal.x = x
				self.list.append(goal)

	def __init__(self, map_):
		self.list = []
		self.map = map_
		for i in range(0, GOAL_COUNT):
				self.add_random_goal(random_goals)
		self.add_random_goal(random_end_goals)

	def get_pending_list(self):
		return [g for g in self.list if not g.done]
