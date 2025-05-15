import os
import json
from . import Manager
from ..utils.fetch_pipeline import Pipeline

class Npm(Manager):
    def parse(self, args):
        pipeline = Pipeline()
        if os.path.isfile(self.cwd + '/package-lock.json'):
            return pipeline.load(self.cwd + '/package-lock.json').parse({ "{packages..dependencies.$}": "{$}" })
        else:
            print('> package-lock.json not found. Looking at package.json instead')
            print('> Warning: actual results maybe incorrect')
            print('> Try "npm i --package-lock-only", add a bit of --force if red texts appear')
            return pipeline.load(self.cwd + '/package.json').parse({ "{dependencies.$}": "{$}" })
