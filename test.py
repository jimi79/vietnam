#!/usr/bin/python3

import math
import curses
import time

def main(stdscr):


	
	y, x = stdscr.getmaxyx()
	oldy = y
	oldx = x
	win = curses.newwin(y - 1, x - 1, 1, 1)
	win.addstr("coucou\n")
	win.addstr("%d %d\n" % (y, x))
	win.refresh() 
	while True:
		y, x = stdscr.getmaxyx()
		if y != oldy or x != oldx:
			oldy = y
			oldx = x
			win.resize(y - 1, x - 1)
			win.addstr("%d %d\n" % (y, x))
		curses.cbreak()
		a = win.getch()
		if a == 'q':
			break

curses.wrapper(main)
