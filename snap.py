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
elif sys.argv[1] == "create":
    snap.create(sys.argv[2:])
elif sys.argv[1] == "restore":
    snap.restore(sys.argv[2])
elif sys.argv[1] == "set":
    snap.setConfig(sys.argv[2:])
elif sys.argv[1] == "help":
    print("update, create, restore, set <key> <value>")