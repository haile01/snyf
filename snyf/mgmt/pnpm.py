import os
import yaml
import json
from . import Manager
from ..utils.fetch_pipeline import Pipeline

class Pnpm(Manager):
    target = 'pnpm-lock.yaml'

    def parse(self, args, flags):
        pipeline = Pipeline()
        if os.path.isfile(self.cwd + '/' + 'pnpm-lock.yaml'):
            target = self.cwd + '/' + 'pnpm-lock.yaml'
            pipeline.load(target)
            deps = pipeline.parse({ "{dependencies.$}": "{specifier}" })
            if deps == {}:
                deps = pipeline.parse({"{importers.{dot}.dependencies.$}": "{specifier}"})

        else:
            print(f'> {self.target} not found. Looking at package.json instead')
            print('> Warning: actual results maybe incorrect')
            target = self.cwd + '/package.json'
            deps = pipeline.load(target).parse({ "{dependencies.$}": "{$}" })

        return { target: deps }
