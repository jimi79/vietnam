# consts
FOREST = "F"
WATER = "W"
BORDER = "B"
NOTHING = "N"
ENNEMIES = "E"

COMMAND_LOOK = "LOOK"
COMMAND_MOVE = "MOVE"
COMMAND_MOVE_ONCE = "MOVE_ONCE"
COMMAND_STOP = "STOP"
COMMAND_WORK = "WORK"
COMMAND_STATUS = "STATUS"
COMMAND_GET_DIRECTIONS = "GET_DIRECTIONS"

ALL_ALIVE_TEAMS_EXITED = "ALL_ALIVE_TEAMS_EXITED"
ALL_TEAMS_EXITED = "ALL_TEAMS_EXITED"
ALL_TEAMS_DEAD = "ALL_TEAMS_DEAD"
ONE_TEAM_DEAD = "ONE_TEAM_DEAD"

# settings

QUERY_DONE = 2 # query complete, could be executed
QUERY_ERR = 1 # key not authorized
QUERY_NEXT = 0 # query not complete

SIZE = 20
CELL_RESOLUTION = 5

COUNT_PLAYER_TEAMS = 3
COUNT_NPC_TEAMS = round(0.1 * SIZE * SIZE)
NPC_TEAMS_AVG_SIZE = (10, 5)
PLAYER_TEAMS_AVG_SIZE = (25, 10)

SPEED_FACTOR = 1 # 1 normal, 2 faster

DEBUG = False
SUPERMAN = False

COUNT_FOREST = round(0.2 * SIZE * SIZE)
COUNT_WATER = round(0.2 * SIZE * SIZE)
COUNT_WONDER = min(9, round(0.05 * SIZE * SIZE)) # max to 9 because in the log, we use numbers from 1 to 9 to reference them. If it's more than 9, it will not be shown on the map
GOAL_COUNT = 2


#debug

if DEBUG:
	#COUNT_FOREST = 0
	#COUNT_WONDER = 2
	#SIZE = 8
	COUNT_WATER = 10
	SPEED_FACTOR = 200 # 1 normal, 2 faster
	#COUNT_NPC_TEAMS = 0
	#GOAL_COUNT = 5
	#SUPERMAN = True
