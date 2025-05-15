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
from .mgmt.pnpm import Pnpm as PnpmMgmt
from .mgmt.pip import Pip as PipMgmt
from .utils.fetch_pipeline import Pipeline

snyk = Snyk()
maven = Maven()
maven_mgmt = MavenMgmt()
npm_mgmt = NpmMgmt()
pnpm_mgmt = PnpmMgmt()
pip_mgmt = PipMgmt()

def test_template():
    # Just to make sure if Snyk keeps the same template format
    test_cases = json.loads(open('test.json', 'r').read())
    for test in test_cases:
        checker = snyk if test['checker'] == 'snyk' else maven
        test['dep'] = test['mgmt'] + '/' + test['dep'] if test['checker'] == 'snyk' else test['dep']
        vulns = checker.check(test['dep'], test['ver'])
        assert json.dumps(vulns) == json.dumps(test['vulns']), 'Template is wrong...'

def test_fetch():
    pipeline = Pipeline()

    pipeline.load('test.yaml')

    schema = {
        "{dependencies.$}": "{specifier}",
    }

    print(pipeline.parse(schema, pretty=True))

def parse_args():
    if len(sys.argv) == 1:
        print('Usage: synf/main.py <npm|maven|test> [target file]')
        exit()
    args = sys.argv[1:]
    mgmt = ''
    deps = {}

    if args[0] == 'test':
        subject = 'template' if len(args) == 1 else args[1]
        if subject == 'template':
            test_template()
        if subject == 'fetch':
            test_fetch()

        exit()

    # Dep manager
    if args[0] == 'npm':
        return 'npm', npm_mgmt.parse(args)
    if args[0] == 'pnpm':
        return 'npm', pnpm_mgmt.parse(args) # NOTE: yep
    if args[0] == 'maven':
        return 'maven', maven_mgmt.parse(args)
    if args[0] == 'pip':
        return 'pip', pip_mgmt.parse(args)

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
