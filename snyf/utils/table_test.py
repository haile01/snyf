from .table import Table

def test():
    cases = [
        # Happy case
        (
            '',
            [
                ['a', 'b', 'a'],
                ['a', 'b', 'a'],
                ['a', 'b', 'a'],
            ]
        ),
        # _huh_ case
        (
            '*||',
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
