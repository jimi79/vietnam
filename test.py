#!/usr/bin/python3

import math
import curses
import time

def main(stdscr):
	print(stdscr)
	curses.halfdelay(10)
	a = stdscr.getch()
	print(a)
	a = stdscr.getch()
	print(a)
	curses.cbreak()
	a = stdscr.getch()

curses.wrapper(main)
