import os
import yaml
import json
from . import Manager
from ..utils.fetch_pipeline import Pipeline

class Pnpm(Manager):
    target = 'pnpm-lock.yaml'

    def parse(self, args, flags):
        pipeline = Pipeline()
        if os.path.isfile(self.cwd + '/' + self.target):
            pipeline.load(self.cwd + '/' + self.target)
            res = pipeline.parse({ "{dependencies.$}": "{specifier}" })
            if res == {}:
                res = pipeline.parse({"{importers.{dot}.dependencies.$}": "{specifier}"})
            
            return res
        else:
            print(f'> {self.target} not found. Looking at package.json instead')
            print('> Warning: actual results maybe incorrect')
            return pipeline.load(self.cwd + '/package.json').parse({ "{dependencies.$}": "{$}" })
