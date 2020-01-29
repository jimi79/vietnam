from goal import *

random_goals = [
	MiddleGoal('build a bridge', 4 * 60),
	MiddleGoal('find a vip', 2 * 60),
	MiddleGoal('destroy an ammunation depot', 1 * 60),
	MiddleGoal('give weapons to a local population', 2 * 60),
	]

random_end_goals = [
	EndGoal('exit point', 30)
]

class Goals(): 
	def add_random_goal(self, list_):
		random.shuffle(list_)
		y, x = self.map.get_goal_location()
		goal = list_.pop()
		goal.y = y
		goal.x = x
		self.list.append(goal)

	def __init__(self, map_):
		self.list = []
		self.map = map_
		self.add_random_goal(random_goals)
		self.add_random_goal(random_end_goals)

