import os
import json
from . import Manager
from ..utils.fetch_pipeline import Pipeline

class Npm(Manager):
    def parse(self, args, flags):
        pipeline = Pipeline()
        found = False 

        if os.path.isfile(self.cwd + '/package-lock.json'):
            target = self.cwd + '/package-lock.json'
            target = pipeline.load(target)
            deps = target.parse({ "{packages..dependencies.$}": "{$}" })
            if len(deps):
                found = True 

        if not found:
            print('> package-lock.json not found, or something weird happened. Looking at package.json instead')
            print('> Warning: actual results maybe incorrect')
            print('> Try "npm i --package-lock-only", add a bit of --force if red texts appear')
            target = self.cwd + '/package.json'
            deps = pipeline.load(target).parse({ "{dependencies.$}": "{$}" })

        return { target: deps }
