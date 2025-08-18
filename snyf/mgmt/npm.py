import os
import json
from . import Manager
from ..utils.fetch_pipeline import Pipeline

class Npm(Manager):
    def parse(self, args, flags):
        pipeline = Pipeline()
        if os.path.isfile(self.cwd + '/package-lock.json'):
            target = self.cwd + '/package-lock.json'
            deps = pipeline.load(target).parse({ "{packages..dependencies.$}": "{$}" })
        else:
            print('> package-lock.json not found. Looking at package.json instead')
            print('> Warning: actual results maybe incorrect')
            print('> Try "npm i --package-lock-only", add a bit of --force if red texts appear')
            target = self.cwd + '/package.json'
            deps = pipeline.load(target).parse({ "{dependencies.$}": "{$}" })

        return { target: deps }
