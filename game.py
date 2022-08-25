#!/usr/bin/python3

import curses
import time
import datetime
import random
import json

import main

def run():
	m = main.Main()
	curses.wrapper(m.run)

run()
