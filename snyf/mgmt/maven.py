import os
import re
from . import Manager

class Maven(Manager):
    def parse(self, args):
        if len(args) == 1:
            print('Usage: snyf/main.py maven <target file>')
            exit()

        path = self.cwd + '/' + args[1]
        if not os.path.isfile(path):
            print('> Target file not found...')
            exit()

        target = open(path, 'r').read()
        target = '\n'.join('' if len(line) and line[0] == '#' else line for line in target.split('\n'))

        deps = self.simple_parse(target)
        if len(deps):
            return deps

        deps = self.mapped_parse(target)
        if len(deps):
            return deps

        raise Exception("Versioning strategy not supported (yet)")

    def simple_parse(self, target):
        deps = {}

        # NOTE: resolve libraries' version
        # E.g:
        # commons-io:commons-io = "1.2.3"

        versions = re.findall(r'([a-z0-9\.\-]+:[a-z0-9\.\-]+)\ ?=\ ?\"?([0-9\-\.a-zA-Z]+)\"?', target)
        for version in versions:
            deps[version[0]] = version[1]

        return deps

    def mapped_parse(self, target):
        deps = {}

        # NOTE: resolve libraries classpath
        # E.g:
        # module = commons-io:commons-io (canonical name)
        # version.ref = commons_io (user-defined)

        res = re.findall(r'(?:module|id) = "(.+?)"\nversion.ref = "(.+?)"', target)
        mapping = {}
        for r in res:
            if r[1] not in mapping:
                mapping[r[1]] = []

            mapping[r[1]].append(r[0])

        # NOTE: Making a _huge_ assumption here...
        # E.g:
        # commons_io = "1.1.1"
        versions = re.findall(r'([a-zA-Z0-9\-]+)\ ?=\ ?\"?([0-9\-\.a-zA-Z]+)\"?', target)
        # print(versions)
        for version in versions:
            if version[0] in mapping:
                for dep in mapping[version[0]]:
                    deps[dep] = version[1]

        return deps
