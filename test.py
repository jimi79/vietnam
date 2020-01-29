#!/usr/bin/python3

import curses

def main(stdscr):
	stdscr.clear()
	stdscr.scrollok(True)
	for i in range(0, 200):
		stdscr.addstr("line %d\n" % i)
	stdscrgT
	stdscr.addstr("line %d\n" % i)
	stdscr.getch()
	
curses.wrapper(main)
