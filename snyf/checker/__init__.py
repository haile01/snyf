from ..utils.table import Table

class Checker:
    def parse(self, args):
        raise Exception("Not implemented")

    def check(self, dep, version):
        raise Exception("Not implemented")

    def render(self, url, vulns):
        print(url)
        color_map = {
            'none': 'b',
            'L': 's',
            'M': 'w',
            'H': 'e',
            'C': 'eb',
        }
        table = Table('|*|')
        for vuln in vulns:
            table.add_row([
                (f"[{vuln['sev']}] {vuln['name']}", color_map[vuln['sev']]),
                vuln['affected'],
                (vuln['url'], 'i')
            ])

        print(table)
