import os
import yaml
import json
from . import Manager
from ..utils.fetch_pipeline import Pipeline

class Pnpm(Manager):
    target = 'pnpm-lock.yaml'

    def parse(self, args):
        pipeline = Pipeline()
        if os.path.isfile(self.cwd + '/' + self.target):
            return pipeline.load(self.cwd + '/' + self.target).parse({ "{dependencies.$}": "{specifier}" })
        else:
            print(f'> {self.target} not found. Looking at package.json instead')
            print('> Warning: actual results maybe incorrect')
            return pipeline.load(self.cwd + '/package.json').parse({ "{dependencies.$}": "{$}" })
