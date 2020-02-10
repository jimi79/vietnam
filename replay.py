#!/usr/bin/python3
from log import *
import argparse

parser = argparse.ArgumentParser('decription=replay the last mission')
parser.add_argument('--speed', type = int, help = 'speed', nargs = '?')
args = parser.parse_args() 
Log().replay(speed = args.speed)
