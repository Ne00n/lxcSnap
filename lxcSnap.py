#!/usr/bin/python3

from Class.snap import SNAP
import sys, os

#path
path = os.path.dirname(os.path.realpath(__file__))
snap = SNAP(path)

if sys.argv[1] == "update":
    snap.update()
elif sys.argv[1] == "create" and len(sys.argv) > 2:
    snap.create(sys.argv[2:])
elif sys.argv[1] == "list" and len(sys.argv) > 2:
    snap.backupsList(sys.argv[2])
elif sys.argv[1] == "download" and len(sys.argv) > 2:
    snap.download(sys.argv[2])
elif sys.argv[1] == "delete" and len(sys.argv) > 2:
    snap.delete(sys.argv[2])
elif sys.argv[1] == "restore" and len(sys.argv) > 2:
    snap.restore(sys.argv[2])
elif sys.argv[1] == "set" and len(sys.argv) > 3:
    snap.setConfig(sys.argv[2:])
elif sys.argv[1] == "help":
    print("update, create <container>, list <container>, download <fid>, delete <fid>, restore <container>, set <key> <value>")
else:
    print("Missing argument, try help")