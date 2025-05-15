import json
import yaml
import toml

class Pipeline:
    def __init__(self, target=None, schema=None):
        self.target = target
        self.schema = schema
        self.raw_data = None

    def load(self, target):
        data = open(target, 'r').read()
        ext = target.split('.')[-1]

        if ext == 'json':
            self.raw_data = json.loads(data)
        elif ext == 'yaml':
            self.raw_data = yaml.safe_load(data)
        elif ext == 'toml':
            self.raw_data = toml.loads(target)
        else:
            raise Exception("Invalid file extension")

        return self

    def parse(self, schema, pretty=False):
        if self.raw_data is None:
            raise Exception("Empty input data")

        res = self.__parse(self.raw_data, schema)
        if pretty:
            res = json.dumps(res, indent=1)

        return res

    def __is_data_path(self, s):
        return type(s) is str and s[0] == '{' and s[-1] == '}'

    def __construct_path(self, s):
        return '{' + '.'.join(s) + '}'

    def __parse(self, context, schema, strict=False, is_spread=False):
        # TODO: Allow some basic string operation to work with pip's requirements.txt and maven's .toml
        if type(schema) is list:
            if type(context) is not list:
                if strict:
                    raise(f"Object {context} is not a list")

                return []

            schema = schema[0]
            res = []
            for element in context:
                res.append(self.__parse(element, schema))

            return res

        elif type(schema) is dict:
            if type(context) is not dict:
                if strict:
                    raise(f"Object {context} is not a list")

                return {}

            res = {}
            for key in schema.keys():
                parsed_key = self.__parse(context, key)
                if type(parsed_key) is list:
                    for p in parsed_key:
                        res[p['value']] = self.__parse(p['context'], schema[key])
                else:
                    if type(schema[key]) is str and '$' in schema[key]:
                        raise Exception("Object value can't spread tho...")

                    res[parsed_key] = self.__parse(context, schema[key])

            return res

        else:
            if schema == '{$}':
                return context

            if self.__is_data_path(schema):
                schema = schema[1:-1]
                schema = schema.split('.')
                tmp = context
                for i in range(len(schema)):
                    attr = schema[i]
                    if attr == '$':
                        if is_spread:
                            raise("Can only spread once for each data path")

                        res = []
                        for key in tmp:
                            value = key if i == len(schema) - 1 else self.__parse(tmp[key], self.__construct_path(schema[i+1:]), is_spread=True)
                            res.append({
                                'value': value,
                                'context': tmp[key]
                            })

                        return res

                    if attr not in tmp:
                        if strict:
                            raise(f"Object {tmp} doesn't contain attribute {attr}")

                        return None

                    tmp = tmp[attr]

                return tmp
            else:
                return schema


    def run(self):
        if self.target is None or self.schema is None:
            raise Exception("Missing input params")

        self.load(self.target)
        return self.parse(self.schema)
