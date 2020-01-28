from goal import *

class Goals(): 
	def add_goal(self):
		self.list.append(Goal())

	def __init__(self):
		self.list = []
		self.add_goal()

