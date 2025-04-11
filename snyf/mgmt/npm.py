import os
import json
from . import Manager

class Npm(Manager):
    def parse(self, args):
        if os.path.isfile(self.cwd + '/package-lock.json'):
            res = {}
            pkgs = json.loads(open(self.cwd + '/package-lock.json').read())
            deps = pkgs['packages']['']['dependencies'].keys()
            for dep in deps:
                dep_path = 'node_modules/' + dep
                if dep_path not in pkgs['packages']:
                    # print(f'> Package {dep} is not here...')
                    continue
                res[dep] = pkgs['packages'][dep_path]['version']

            deps = res
        else:
            print('> package-lock.json not found. Looking at package.json instead')
            print('> Warning: actual results maybe incorrect')
            print('> Try "npm i --package-lock-only", add a bit of --force if red texts appear')
            pkgs = json.loads(open(cwd + '/package.json').read())
            deps = pkgs['dependencies']

        return deps
