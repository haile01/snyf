import re
import requests
from . import Checker

class Maven(Checker):
    def __init__(self):
        super().__init__()
        self.name = 'Maven'

        self.vuln_template = re.compile(r"""
            <a class="vuln" href="https://cve\.mitre\.org.+?>(.+?)</a>
        """.replace('\n', '').replace('    ', '').strip())

    def check_dep(self, dep, ver):
        dep = dep.replace(':', '/')
        url = f'https://mvnrepository.com/artifact/{dep}/{ver}'
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        }
        r = requests.get(url, headers=headers)
        pos = r.text.find('Vulnerabilities from dependencies')

        direct = re.findall(self.vuln_template, r.text[:pos])
        # Dun care for now
        transitive = re.findall(self.vuln_template, r.text[pos:])

        if len(direct) == 0:
            return

        data = []
        print("\033[96m= Direct vulnerabilities from Maven repo =\033[0m")
        for vuln in direct:
            data.append({
                'name': vuln,
                'sev': 'none',
                'affected': ' ', # TODO
                'url': 'https://cve.mitre.org/cgi-bin/cvename.cgi?name' + vuln
            })

        self.update(f'{dep}@{ver}', url, data)

        return data
