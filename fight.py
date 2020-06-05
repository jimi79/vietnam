import tools
import copy
from team import *

class Fight():
    def __init__(self, map_, teams1, teams2):
        self.map_ = map_
        self.teams1 = [t for t in copy.copy(teams1.list) if isinstance(t, TeamInfantry)]
        self.teams2 = [t for t in copy.copy(teams2.list) if isinstance(t, TeamInfantry)]
        for t in self.teams1:
            if t.fighting:
                t.still_fighting = False
        for t in self.teams2:
            if t.fighting:
                t.still_fighting = False

    def kill(self, teams, count):
        left_to_kill = count
        debug("someone will kill %d" % count)
        for t in teams:
            killed_in_that_team = min(t.count, count // len(teams))
            t.count = t.count - killed_in_that_team
            debug("%d ppl removed from team %s" % (killed_in_that_team, t.nato))
            left_to_kill = left_to_kill - killed_in_that_team

        if left_to_kill > 0 and len(teams) > 1: # if one team, we didn't divide, so there is no way there are ppl left to kill
            debug("we need to remove more ppl")
            for t in teams:
                killed_in_that_team = min(t.count, left_to_kill)
                t.count = t.count - killed_in_that_team
                debug("%d ppl removed from team %s" % (killed_in_that_team, t.nato))
                left_to_kill = left_to_kill - killed_in_that_team
                if left_to_kill == 0:
                    break

    def update_command_list(self, t):
        if not t.fighting:
            c = [c for c in t.commands.list if isinstance(t, CommandFight)]
            if len(c) == 0:
                t.commands.add(CommandFight(t.count))
                debug("adding task fight for team %s" % t.nato)
                t.fighting = True

        t.still_fighting = True

    def fight(self, t1, t2):
        debug("Fight between:")
        for t in t1:
            self.update_command_list(t)
            debug("on my left: %s" % t.nato)

        for t in t2:
            self.update_command_list(t)
            debug("on my right: %s" % t.nato)

        count1 = sum([t.count for t in t1])
        count2 = sum([t.count for t in t2])
        if count1 > 0 and count2 > 0:
            killed_by_1 = min(count2, random.randrange(0, count1))
            killed_by_2 = min(count1, random.randrange(0, count2))
            debug("left team will kill %d ppl" % killed_by_1)
            debug("right team will kill %d ppl" % killed_by_2)
            self.kill(t2, killed_by_1)
            self.kill(t1, killed_by_2)

    def build_list_on_that_cell(self, teams, x, y):
        r = []
        temp = copy.copy(teams)
        while len(temp) > 0:
            t = temp.pop()
            if t.x == x and t.y == y:
                r.append(t)
        return r

    def get_alive_count(self, teams):
        return sum([t.count for t in teams])

    def run(self):
        temp = copy.copy(self.teams1)
        while len(temp) > 0:
            t = temp.pop()
            t1 = self.build_list_on_that_cell(self.teams1, t.x, t.y)
            t2 = self.build_list_on_that_cell(self.teams2, t.x, t.y)
            if self.get_alive_count(t2) > 0 and self.get_alive_count(t1) > 0: # t1 team could be all dead
                self.fight(t1, t2)

        self.clean(self.teams1)
        self.clean(self.teams2)

    def clean(self, teams):
        for t in teams:
            if t.fighting and not t.still_fighting:
                debug("removing task fight for team %s" % t.nato)
                t.fighting = False
                c = [c for c in t.commands.list if isinstance(c, CommandFight)] # should exists
                if len(c) > 0:
                    command = c[0]
                    if t.get_alive():
                        loss = command.count_before - t.count
                        if loss == 0:
                            t.add_reply("we just had a fight but we suffer no loss")
                        elif loss == 1:
                            t.add_reply("we just had a fight and we lost one guy")
                        else:
                            t.add_reply("we just had a fight and we lost %d peoples" % (command.count_before - t.count))
                    if len(c) > 0:
                        t.commands.list.remove(command)




class TimedFight():
    def __init__(self):
        self.last_fight_time = datetime.datetime.now()

    def check(self, map_, teams1, teams2):
        if self.last_fight_time + datetime.timedelta(seconds = 10 / SPEED_FACTOR) < datetime.datetime.now(): # every 10 minutes in game
            self.last_fight_time = datetime.datetime.now()

            Fight(map_, teams1, teams2).run() # will also handle the command
