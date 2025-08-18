import os

class Manager:
    def __init__(self):
        self.cwd = os.getcwd()

    def parse(self, args, flags):
        # NOTE: Schema:
        # {
        #   "path-to-dependency-file": {
        #       "dependency-name": "version"
        #   }
        # }
        #
        raise Exception("Not implemented")
