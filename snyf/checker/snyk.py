import re
import requests
from . import Checker

class Snyk(Checker):
    def __init__(self):
        super().__init__()
        self.name = 'Snyk'

        self.vuln_template = re.compile(r"""
            <tr.+?>
                <td.+?>
                    <ul.+?><li.+?><abbr.+?>\s*(?P<sev>[A-Z])\s*<\/abbr><\/li><\/ul>
                    <a.+? href="\/vuln\/(?P<tag>[A-Za-z0-9\-]+?)".+?>
                        (?P<vuln_name>.+?)
                    <\/a>
                    (?P<body>[\s\S]+?)
                <\/td>
                <td.+?>
                    <div class="vulnerable-versions".+?>
                        (?P<vuln_ver>.+?)
                    <\/div>
                <\/td>
            <\/tr>
        """.replace('\n', '').replace('    ', '').strip())

        self.version_template = re.compile(r"""
            <span.+?>(.+?)</span>
        """.replace('\n', '').replace('    ', '').strip())

        self.parsed_version_template = re.compile(r"""
            title="([\[\(][0-9a-zA-Z\-\.]*,[0-9a-zA-Z\-\.]*[\]\)])
        """.replace('\n', '').replace('    ', '').strip())

    def clean_comment(self, text):
        return text.replace('<!--]-->', '').replace('<!--[-->', '').replace('<!---->', '')

    def parse_vers(self, vers):
        res = []
        # NOTE: In case Snyk did that for us alr
        parsed = re.findall(self.parsed_version_template, vers)
        if len(parsed):
            return ' '.join(parsed)

        vers = re.findall(self.version_template, vers)
        for ver in vers:
            ver = ver.replace('&lt;', '<').replace('&gt;', '>')
            constraints = ver.split(' ')
            tmp = {}
            cur = ''
            for c in constraints:
                if c == '*':
                    # This lib is fcked hard
                    continue

                key = 'upper' if c[0] == '<' else 'lower'
                if c[1] == '=':
                    tmp[key] = {'value': c[2:], 'eq': True}
                else:
                    tmp[key] = {'value': c[1:], 'eq': False}

            if 'lower' in tmp:
                cur += '[' if tmp['lower']['eq'] else '('
                cur += tmp['lower']['value'] + ','
            else:
                cur += '(,'

            if 'upper' in tmp:
                cur += tmp['upper']['value']
                cur += ']' if tmp['upper']['eq'] else ')'
            else:
                cur += ')'

            res.append(cur)

        return ' '.join(res)

    def format(self, vuln):
        res = ''
        sev, tag, vuln_name, body, vuln_ver = vuln

        if sev == 'L':
            res += '\033[92m v[L] '
        elif sev == 'M':
            res += '\033[93m -[M] '
        else:
            res += '\033[91m ^[H] '

        res += vuln_name + '\033[0m '
        res += self.parse_vers(vuln_ver) + ' '
        res += 'https://security.snyk.io/vuln/' + tag + ' '

        return res

    def check_dep(self, dep, ver):
        url = f'https://security.snyk.io/package/{dep}/{ver}'
        r = requests.get(url)
        vulns = re.findall(self.vuln_template, self.clean_comment(r.text))

        if not vulns:
            return

        data = []
        for vuln in vulns:
            sev, tag, vuln_name, body, vuln_ver = vuln
            sev_map = {
                'L': 'low',
                'M': 'medium',
                'H': 'high',
                'C': 'critical'
            }
            data.append({
                'name': vuln_name,
                'sev': sev,
                'affected': self.parse_vers(vuln_ver),
                'url': 'https://security.snyk.io/vuln/' + tag
            })

        self.update(f'{dep}@{ver}', url, data)
        return data
