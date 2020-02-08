This is a game. A very approximate simulation of the vietnam war, only in text.
The screen is separated in two zones: 
  top: log of radio
  bottom: commands sent to your teams
  
# Teams
You have 4 teams:
  Alpha, Bravo and Charly: infantry team, on ground
  Delta: Helicopter
  Infantry teams are dropped randomly (let's say they were parachuted) on a field.

# What they can do:
* look to look around
they will tell you what they see in 8 directions: north, north east, east, south east, south, south-west, west, north-west
* status
they will tell you the number of ppl alive in the team (randomly attributed at start), and if they are doing somethg at the moment
* move
then you give them a direction
* work
if there is somethg to be done here, any of the team can do it, unless some other team is already working on it.
* stop
stop what they are doing
* move for 5 km
move for a short distance. easier to handle when u're commanding than the other move instruction, which instructs them to move until they can't continue.

# what the Helicopter can do:
* get directions / reckon
they will report you the direction of each team to each objective

# objectives:
* there are 3 objects: 
2 randoms, like getting intel for vietcongs (it's a goal that has to be completed, but doesn't give you any extra stuff)
and exit, which is required to get a lift from some heli to get out of the war zone.

# how it works:
## completion
press tab to get a list of what you can do.
For ex, if you press tab a start, the game will add in the log the list of the team.
## giving an order:
press the team name, and the command
if the command is moving, then also give the direction, using the keys like so

q w e      q is north-west, w is north, e is north-east
a   d      a is west, d is east
z x c      z is south-weast, x is south, c is south-east
## teams commands
the team keep a list of tasks to do.
*look* and *status* will become the first task when requested. it will delay other tasks.
*moving*, *moving for 5 km*, *working* will erase the last *moving*, *moving for 5 km*, *working* command
if a fight occure, all other commands are erased.
## heli command
the heli can only go on reckon missions. here are the steps of a reckon mission
* taking off
* reporting position of each team compared to each goal left to be done
* going back
* refuelling
if you request a new reckon mission while one is in progress, the team will report you why it can't do it at that moment.
## map
the map is consituted of 3 things
* water
water can't be crossed
* plain
* forest
* wonders
wonders are famous real place in vietnam. a water cell may be replaced by a wonder like Con Dao Islands (doesn't make it any more passable). a non water place can be replaced by a wonder like the Temple of Literature. 
## fight
Once one or multiple teams of yours happen to be close to one or multiple ennemy teams, a fight occurs.
The outcome is related to the number of ppl fighting, so you may want to have multiples teams at the same place to get more chances of winning.
## visibility
you can see only from a certain distance. so it's not because you don't see any ennemies that they won't be at your place at some point.
also something good to know: your teams can't see neither ennemies or any other of your teams.

# Example of a game

**in bold, pressed key**
**tab**
day 1 00:11: a: team alpha, b: team bravo, c: team charly, d: team delta
**a, tab**
day 1 02:20: l: look, t: status, s: stop, w: work, M: move, m: move for 5 km
**t**
  day 1 04:26: you: team alpha, status
day 1 05:16: alpha: we are 22 people.
**al**
  day 1 05:45: you: team alpha, look
day 1 06:35: alpha: we see: NE: some water. SE: around 10 soldiers. S: some water. NW: some water.
**amd**
  day 1 09:59: you: team alpha, move for 5 km east
**at**
  day 1 11:21: you: team alpha, status
day 1 12:12: alpha: we are 22 people. we are moving.
day 1 13:02: alpha: we are at the new location.
*the look command is automatically executed after a team stops moving*
day 1 13:53: alpha: we see: N: some water. SE: a village. SW: some water.

**A team will cease to respond to you once all its members are killed**

# ennemies
Ennemies are teams like yours, except they will try to kill you on sight.
On a fight happens, you will have no feedback as your team is busy fighting.
You may have a report at the end of the fight, but only if it's win by your team.

# Internal mechanics
## ennemies
ennemies are placed randomly, and they can move around their initial position at very random moments (but at least one hour to go from one place to another)
ennemies won't follow you at any point, they will just patrol around and get into a fight if you happen to be at the same place as they are.
if u want to play it safe:
* have multiples teams of yours at one point
but it's not easy because: 
** you need to know where they are one to each other
** they won't have the same walking speed
* avoid forests
* look very often
a ennemy cannot move more than three cells in total, so if you see it (meaning it's one cell away), you can move two cells away from it, it won't reach you in any case.
