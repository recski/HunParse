#!/usr/bin/python
import sys
print sum([int(line.split()[0]) for line in sys.stdin]) 
