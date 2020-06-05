#!/usr/bin/python3

import curses
import time
import datetime
import random
import json

from main import *
from tools import *
from command import *


def run():
    m = Main()
    curses.wrapper(m.run)

run()
