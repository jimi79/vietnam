#!/usr/bin/python3

import curses
import time
import datetime
import random
import json

from main import *
from tools import *
from command import *
from const import *


# forest: invisible but can't see
# moving: defence = 0.5
# defending: defence = 1



def test_query(): 
	q = Query(Teams(2, Map_()))
	assert q.test_key('2') == QUERY_NEXT
	assert q.test_key('L') == QUERY_DONE
	print(q.query)

	q = Query(Teams(2, Map_()))
	assert q.test_key('1') == QUERY_NEXT
	assert q.test_key('M') == QUERY_NEXT
	assert q.test_key('w') == QUERY_DONE
	print(q.query)

def test_commands():
	a = Commands()
	a.add(CommandMove())
	assert(a.get_debug_letters() == 'M')
	a.add(CommandLook())
	assert(a.get_debug_letters() == 'LM')
	a.add(CommandLook())
	assert(a.get_debug_letters() == 'LM')
	a.add(CommandStop())
	assert(a.get_debug_letters() == 'SLM') # once executed, stop will remove everythg
	a.add(CommandFight())
	assert(a.get_debug_letters() == 'F') # fight removes everythg by design
	a.add(CommandStop())
	assert(a.get_debug_letters() == 'F') # shouldn't be able to stop here

def test_with_delay():
# not logical, if i append somethg that should be done. but still, that will work
	a = Commands()
	a.add(CommandMove())
	assert(a.get_debug_letters() == 'M')
	time.sleep(2)
	a.add(CommandLook())
	assert(a.get_debug_letters() == 'LM')

#test_commands()
test_with_delay()

