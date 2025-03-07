import re
import requests
from . import Checker

class Snyk(Checker):
    def __init__(self):
        self.vuln_template = re.compile("""
            <tr.+?>
            <td.+?>
            <ul.+?>
            <li.+?>
            <abbr.+?>
             (?P<sev>[A-Z])<\/abbr>
            <\/li>
            <\/ul>
            <a.+? href="\/vuln\/(?P<tag>[A-Za-z0-9\-]+?)".+?>
            (?P<vuln_name>.+?)
            <\/a>
            <div.+?>
            <div.+?>
            <p>(?P<title>[\s\S]+?)<\/p>
            \s+?<p>(?P<desc>[\s\S]+?)<\/p>
            \s+?<\/div>
            <p.+?>.+?<\/p>
            <div.+?>
            <p>(?P<fix>[\s\S]+?)<\/p>
            \s+?<\/div>
            <\/div>
            <\/td>
            <td.+?>
            <div class="vulnerable-versions".+?>
            (?P<vuln_ver>.+?)
            <\/div>
            <\/td>
            <\/tr>
        """.replace('\n', '').replace('    ', '').strip())

        self.version_template = re.compile("""
            <span.+?><span.+?title="(.+?)".+?</span>.*?</span>
        """.replace('\n', '').replace('    ', '').strip())

    def clean_comment(self, text):
        return text.replace('<!--]-->', '').replace('<!--[-->', '').replace('<!---->', '')

    def format(self, vuln):
        res = ''
        sev, tag, vuln_name, title, desc, fix, vuln_ver = vuln

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

    def parse_vers(self, vers):
        res = []
        vers = re.findall(self.version_template, vers)
        for ver in vers:
            ver = ver.replace('&lt;', '<').replace('&gt;', '>')
            constraints = ver.split(' ')
            tmp = {}
            cur = ''
            for c in constraints:
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

    def check(self, dep, ver):
        url = f'https://security.snyk.io/package/{dep}/{ver}'
        r = requests.get(url)
        vulns = re.findall(self.vuln_template, self.clean_comment(r.text))

        if not vulns:
            return

        print("\033[96m= Vulnerabilities from Snyk =\033[0m")
        for vuln in vulns:
            print(self.format(vuln))

        return vulns
