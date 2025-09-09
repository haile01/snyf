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
from .mgmt.gradle import Gradle as GradleMgmt
from .mgmt.npm import Npm as NpmMgmt
from .mgmt.pnpm import Pnpm as PnpmMgmt
from .mgmt.pip import Pip as PipMgmt
from .utils.fetch_pipeline import Pipeline
from .utils.parse_args import parse_args
from .test import parse_test

snyk = Snyk()
maven = Maven()
maven_mgmt = MavenMgmt()
gradle_mgmt = GradleMgmt()
npm_mgmt = NpmMgmt()
pnpm_mgmt = PnpmMgmt()
pip_mgmt = PipMgmt()

def parse_deps():
    available_parsers = {
        'npm': npm_mgmt.parse,
        'pnpm': pnpm_mgmt.parse,
        'maven': maven_mgmt.parse,
        'gradle': gradle_mgmt.parse,
        'pip': pip_mgmt.parse,
    }

    parser, mgmt, args, flags = parse_args(available_parsers)
    deps = parser(args, flags)

    return mgmt, deps

if __name__ == "__main__":
    parse_test()
    mgmt, deps = parse_deps()

    dep_cnt = 0
    for path in deps:
        dep_cnt += len(deps[path])

    print(f'> Found {str(dep_cnt)} direct dependencies')

    for path in deps:
        snyk.header(path)
        if mgmt == "maven":
            maven.header(path)

        for dep in deps[path]:
            ver = deps[path][dep]
            print("=====\033[95m", dep, ver, "\033[0m=====")
            if ver[0] == '^':
                # NOTE: only happen when package-lock.json is f-ed up, so anw...
                ver = ver[1:]

            snyk.check(mgmt + '/' + dep, ver)
            if mgmt == "maven":
                maven.check(dep, ver)

    snyk.render()
    if mgmt == "maven":
        maven.render()
