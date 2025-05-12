import os
import json
from . import Manager

class Pip(Manager):
    def parse(self, args):
        if os.path.isfile(self.cwd + '/requirements.txt'):
            res = {}
            pkgs = open(self.cwd + '/requirements.txt').read().strip().split('\n')
            deps = {}
            for dep in pkgs:
                dep = dep.split('==')
                deps[dep[0]] = dep[1]

        else:
            print('> requirements.txt not found')
            exit()

        return deps
