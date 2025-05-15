import os
import yaml
import json
from . import Manager

class Pnpm(Manager):
    target = 'pnpm-lock.yaml'

    def parse(self, args):
        if os.path.isfile(self.cwd + '/' + self.target):
            deps = {}
            pkgs = yaml.safe_load(open(self.cwd + '/' + self.target).read())
            for dep in pkgs['dependencies']:
                deps[dep] = pkgs['dependencies'][dep]['specifier']

        else:
            print(f'> {self.target} not found. Looking at package.json instead')
            print('> Warning: actual results maybe incorrect')
            pkgs = json.loads(open(self.cwd + '/package.json').read())
            deps = pkgs['dependencies']

        return deps
