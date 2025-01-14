import requests
import re
import os
import json

HOST = 'https://security.snyk.io/package/npm'
cwd = os.getcwd()
deps = json.loads(open(cwd + '/package.json').read())['dependencies']

vuln_template = """
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
"""
vuln_template = re.compile(''.join(vuln_template.split('\n')).strip())

version_template = """
<span.+?><span.+?title="(.+?)".+?</span>.+?</span>
"""
version_template = re.compile(''.join(version_template.split('\n')).strip())

def clean_comment(text):
	return text.replace('<!--]-->', '').replace('<!--[-->', '').replace('<!---->', '')

def check(dep, ver):
	r = requests.get(f'{HOST}/{dep}/{ver}')
	vulns = re.findall(vuln_template, clean_comment(r.text))
	
	return vulns if vulns else []

def parse_vers(vers):
	res = []
	vers = re.findall(version_template, vers)
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

def format(vuln):
	res = ''
	sev, tag, vuln_name, title, desc, fix, vuln_ver = vuln

	if sev == 'L':
		res += 'v[L] '
	elif sev == 'M':
		res += '-[M] '
	else:
		res += '^[H] ' 

	res += vuln_name + ' '
	res += parse_vers(vuln_ver) + ' ' 
	res += 'https://security.snyk.io/vuln/' + tag + ' '


	return res

def test():
	# Just to make sure if Snyk keeps the same template format
	vulns = check('axios', '0.21.1')
	assert json.dumps(vulns) == open('test.json', 'r').read(), 'Template is wrong...' 

if __name__ == "__main__":
	for dep in deps:
		ver = deps[dep]
		print("=====", dep, ver, "=====")
		if ver[0] == '^':
			ver = ver[1:]
		
		vulns = check(dep, ver)
		for vuln in vulns:
			print(format(vuln))
