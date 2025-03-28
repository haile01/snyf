import requests
import re
import os
import json
import sys
import importlib
from pathlib import Path

# NOTE: PEP366 thingy magingy
def import_parents(level=1):
    global __package__
    file = Path(__file__).resolve()
    parent, top = file.parent, file.parents[level]

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError: # already removed
        pass

    __package__ = '.'.join(parent.parts[len(top.parts):])
    importlib.import_module(__package__) # won't be needed after that

if __name__ == '__main__' and __package__ is None:
    import_parents()

from .checker.snyk import Snyk
from .checker.maven import Maven
from .mgmt.maven import Maven as MavenMgmt
from .mgmt.npm import Npm as NpmMgmt

snyk = Snyk()
maven = Maven()
maven_mgmt = MavenMgmt()
npm_mgmt = NpmMgmt()

def test():
    # Just to make sure if Snyk keeps the same template format
    test_cases = json.loads(open('test.json', 'r').read())
    for test in test_cases:
        checker = snyk if test['checker'] == 'snyk' else maven
        test['dep'] = test['mgmt'] + '/' + test['dep'] if test['checker'] == 'snyk' else test['dep']
        vulns = checker.check(test['dep'], test['ver'])
        assert json.dumps(vulns) == json.dumps(test['vulns']), 'Template is wrong...'

    exit()

def parse_args():
    if len(sys.argv) == 1:
        print('Usage: synf/main.py <npm|maven|test> [target file]')
        exit()
    args = sys.argv[1:]
    mgmt = ''
    deps = {}

    if args[0] == 'test':
        test()
        exit()

    # Dep manager
    if args[0] == 'npm':
        return 'npm', npm_mgmt.parse(args)
    elif args[0] == 'maven':
        return 'maven', maven_mgmt.parse(args)
    else:
        raise Exception('Unsupported dependency manager...')

if __name__ == "__main__":
    mgmt, deps = parse_args()
    print(f'> Found {str(len(deps))} direct dependencies')
    for dep in deps:
        ver = deps[dep]
        print("=====\033[95m", dep, ver, "\033[0m=====")
        if ver[0] == '^':
            # NOTE: only happen when package-lock.json is f-ed up, so anw...
            ver = ver[1:]

        snyk.check(mgmt + '/' + dep, ver)
        if mgmt == "maven":
            maven.check(dep, ver)
