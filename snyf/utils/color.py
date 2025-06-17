class Color:
    def __init__(self, codes):
        if type(codes) is str:
            self.codes = [codes]
        elif type(codes) is list:
            self.codes = codes
        else:
            raise Exception('bruh')

    def p(self, s):
        return ''.join(self.codes) + s + ''.join(['\033[0m'] * len(self.codes))
