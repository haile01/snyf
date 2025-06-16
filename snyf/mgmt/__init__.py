import os

class Manager:
    def __init__(self):
        self.cwd = os.getcwd()

    def parse(self, args, flags):
        raise Exception("Not implemented")
