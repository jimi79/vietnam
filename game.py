#!/usr/bin/python3

import curses
import time
import datetime
import random
import json

from main import *
from tools import *


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

def run():
	m = Main()
	curses.wrapper(m.run)
		
run()
