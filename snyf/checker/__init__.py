class Checker:
    def parse(self, args):
        raise Exception("Not implemented")

    def check(self, dep, version):
        raise Exception("Not implemented")

    def render(self, url, vulns):
        print(url)
        data = []
        color = {
            'low': '\033[92m',
            'medium': '\033[93m',
            'high': '\033[91m',
            'none': '\033[1m',
            'close': '\033[0m'
        }
        for vuln in vulns:
            row = []
            row.append(color[vuln['sev']] + vuln['name'] + color['close'])
            row.append(vuln['affected'])
            row.append(vuln['url'])
            data.append(row)

