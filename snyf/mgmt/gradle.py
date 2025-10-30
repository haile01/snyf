import os
import re
import pathlib
from . import Manager

class Gradle(Manager):
    def parse(self, args, flags):
        if len(args) == 1:
            print('Usage: snyf/main.py gradle')
            exit()

        deps = {}
        for path in pathlib.Path('.').glob('**/build.gradle*'):
            path = self.cwd + '/' + str(path)
            target = open(path, 'r').read()

            tmp_deps = {}

            # NOTE: resolve version vars
            vars = re.findall(r'val\ ([a-zA-Z0-9_])\ =\ "?([0-9]\.)+"?', target)

            # NOTE: match "resolvable" dep versions
            versions = re.findall(r'implementation\("([a-z0-9\.\-]+:[a-z0-9\.\-]+):\$([a-zA-Z0-9_]+)"\)', target)
            versions += re.findall(r'implementation\s*\'([a-z0-9\.\-]+:[a-z0-9\.\-]+):\$([a-zA-Z0-9_]+)\'', target)
            for version in versions:
                if version[1] in vars:
                    tmp_deps[version[0]] = vars[version[1]]

            # NOTE: match dep with defined versions
            versions = re.findall(r'implementation\("([a-z0-9\.\-]+:[a-z0-9\.\-]+):([0-9\.]+)"\)', target)
            versions = re.findall(r'implementation\s*\'([a-z0-9\.\-]+:[a-z0-9\.\-]+):([0-9\.]+)\'', target)
            for version in versions:
                tmp_deps[version[0]] = version[1]

            deps[path] = tmp_deps

        return deps
