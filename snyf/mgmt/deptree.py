import os
import re
import pathlib
from . import Manager

class DepTree(Manager):
    def parse(self, args, flags):
        if len(args) == 1:
            print('Usage: snyf/main.py deptree')
            exit()

        deps = {}
        for path in pathlib.Path('.').glob('**/dependencies.txt'):
            path = self.cwd + '/' + str(path)
            target = open(path, 'r').read()

            tmp_deps = {}

            # NOTE: match dep with defined versions
            versions = re.findall(r'([a-z0-9\.\-]+:[a-z0-9\.\-]+):([0-9\.]+)', target)
            for version in versions:
                tmp_deps[version[0]] = version[1]

            deps[path] = tmp_deps

        return deps
