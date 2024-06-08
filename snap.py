#!/usr/bin/python3

from Class.snap import SNAP
import sys, os

#path
path = os.path.dirname(os.path.realpath(__file__))
snap = SNAP(path)

if len(sys.argv) == 1:
    print("Missing argument")
elif sys.argv[1] == "update":
    snap.update()