import random
from tools import *
from const import *

class Goal():
    def __init__(self, name, duration):
        self.name = name # building a bridge
        self.in_progress = False # if true, then if a command 'work' is happening, the team will say 'no, someone is taking care of it'
        self.duration = duration / SPEED_FACTOR # duration of the task
        #self.team_letter_ids_required = None
#note: only first team can do some task (let's say they are the only competent)
        self.done = False

class MiddleGoal(Goal):
    def __init__(self, name, duration):
        super().__init__(name, duration)
        #self.team_letter_ids_required = ['a']

class EndGoal(Goal):
    def __init__(self, name, duration):
        super().__init__(name, duration)
