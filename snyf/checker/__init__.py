from ..utils.table import Table

class Checker:
    def __init__(self):
        self.table = Table('|*|')
        self.show = False

    def parse(self, args):
        raise Exception("Not implemented")

    def check(self, dep, version):
        raise Exception("Not implemented")

    def update(self, name, url, vulns):
        color_map = {
            'none': 'b',
            'L': 's',
            'M': 'w',
            'H': 'e',
            'C': 'eb',
        }
        self.table.add_row([
            (name, 'hb'),
            (url, 'i--')
        ], True)
        for vuln in vulns:
            if not self.show:
                self.show = True

            self.table.add_row([
                (f"[{vuln['sev']}] {vuln['name']}", color_map[vuln['sev']]),
                vuln['affected'],
                (vuln['url'], 'i')
            ])

    def render(self):
        if self.show:
            print(f"\033[96m= Vulnerabilities from {self.name} =\033[0m")
            print(self.table)
        else:
            print(f"\033[96mFound no vulnerabilities from {self.name}\033[0m")
