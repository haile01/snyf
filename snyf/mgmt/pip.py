import os
import sys
import json
from . import Manager

class Pip(Manager):
    def parse(self, args, flags):
        if flags.get('pip-resolve'):
            deps = self.resolve()

        if os.path.isfile(self.cwd + '/requirements.txt'):
            res = {}
            pkgs = open(self.cwd + '/requirements.txt').read().strip().split('\n')
            deps = {}
            for dep in pkgs:
                if '==' not in dep:
                    print(f'Seems like "{dep}" is not an exact version')
                    prompt = input('Do you want to borrow \033[1mpip\033[0m a hand to resolve this? (y/n) ')
                    if prompt.strip().lower() == 'y':
                        return self.resolve()
                    else:
                        print('Fair enough')
                        print('\033[3mdies\033[0m')
                        exit()

                dep = dep.split('==')
                deps[dep[0]] = dep[1]

        else:
            print('> requirements.txt not found')
            exit()

        target = self.cwd + '/requirements.txt'
        return { target: deps }

    def resolve(self):
        # NOTE: if this gets command injection it's Python's problem not mine ;-;
        os.system(f'{sys.executable} -m pip install --dry-run -r requirements.txt --report /tmp/requirements.json')

        pkgs = json.loads(open('/tmp/requirements.json', 'r').read())['install']
        deps = {}
        for dep in pkgs:
            if not dep['requested'] and not dep['is_direct']:
                continue

            dep = dep['metadata']
            deps[dep['name']] = dep['version']

        return deps
