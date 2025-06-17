import sys
from .utils.table import Table

def parse_test():
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        subject = 'template' if len(sys.argv) == 2 else sys.argv[2]
        if subject == 'template':
            test_template()
        if subject == 'fetch':
            test_fetch()
        if subject == 'table':
            test_table()

        exit()

def test_template():
    # Just to make sure if Snyk keeps the same template format
    test_cases = json.loads(open('test.json', 'r').read())
    for test in test_cases:
        checker = snyk if test['checker'] == 'snyk' else maven
        test['dep'] = test['mgmt'] + '/' + test['dep'] if test['checker'] == 'snyk' else test['dep']
        vulns = checker.check(test['dep'], test['ver'])
        assert json.dumps(vulns) == json.dumps(test['vulns']), 'Template is wrong...'

    print('\033[92m \033[1m Test ran successfully \033[0m \033[0m')

def test_fetch():
    pipeline = Pipeline()

    pipeline.load('test.yaml')

    schema = {
        "{dependencies.$}": "{specifier}",
    }

    print(pipeline.parse(schema, pretty=True))

def test_table():
    cases = [
        # Happy case
        (
            'w||s|',
            [
                [('a', 'u'), 'b', 'a', 'ahihi'],
                ['a', 'b', ('a', 'h')],
                ['a', ('b', 'b'), 'a'],
            ]
        ),
        # _huh_ case
        (
            '*e|w|ib',
            [
                ['a' * 100, 'b', 'a', ('ahihi', 'bold')],
                ['a', 'b' * 200, 'a'],
                ['a', 'b', 'a' * 200],
            ]
        ),
        # fail case
        (
            '*|*|',
            [
                ['a' * 100, 'b', 'a'],
                ['a', 'b' * 200, 'a'],
                ['a', 'b', 'a' * 200],
            ]
        ),
    ]
    for t in cases:
        table = Table(format=t[0])
        table.add_rows(t[1])
        print(table)
        print("-------")
