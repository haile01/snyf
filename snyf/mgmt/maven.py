import os
import re
import toml
from . import Manager

class Maven(Manager):
    def parse(self, args):
        if len(args) == 1:
            print('Usage: snyf/main.py maven <target file>')
            exit()

        is_toml = args[1][-5:] == ".toml"

        path = self.cwd + '/' + args[1]
        if not os.path.isfile(path):
            print('> Target file not found...')
            exit()

        target = open(path, 'r').read()

        if is_toml:
            deps = self.toml_parse(target)
            if len(deps):
                return deps

        else:
            target = '\n'.join('' if len(line) and line[0] == '#' else line for line in target.split('\n'))
            deps = self.simple_parse(target)
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

    def toml_parse(self, target):
        deps = {}

        # NOTE: resolve libraries classpath & versions
        # Making a _huge_ assumption in schema here
        # E.g:
        # module = commons-io:commons-io (canonical name)
        # version.ref = commons_io (user-defined)
        # ...
        # commons_io = "1.1.1"

        target = toml.loads(target)
        versions = target['versions']
        libs = target['libraries']

        for name in libs:
            lib = libs[name]
            if 'module' in lib:
                dep_name = lib['module']
            elif 'group' in lib:
                dep_name = lib['group'] + ':' + lib['name']
            else:
                print(f'\033[1m[ERROR] Can\'t resolve {name}\033[0m')
                continue

            if 'version' not in lib:
                print(f'\033[1m[INFO] Ignore {name} since no version number\033[0m')
                continue

            if type(lib['version']) is str:
                ver_num = lib['version']
            else:
                ref = lib['version']['ref']
                if ref in versions:
                    ver_num = versions[ref]
                else:
                    print(f'\033[1m[ERROR] Can\'t resolve {name}\033[0m')
                    continue

            deps[dep_name] = ver_num

        return deps
