import subprocess, sys, os

class SNAP():

    def __init__(self,path):
        self.path = path

    def update(self):
        subprocess.run("cd; git pull",shell=True)
