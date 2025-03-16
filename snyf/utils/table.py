import os

class Table:
    def __init__(self):
        self.colors = {
            'header': '\033[95m',
            'primary': '\033[94m',
            'info': '\033[96m',
            'success': '\033[92m',
            'warning': '\033[93m',
            'error': '\033[91m',
            'end': '\033[0m',
            'bold': '\033[1m',
            'underline': '\033[4m'
        }
        self.width = os.get_terminal_size()[0]
        self.col_cnt = 0
        self.header = False

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)

    def add_row(self, row):
        self.col_cnt = max(self.col_cnt, len(row))
        self.rows.append(row)

    def allocate(self):
        # TODO
        pass

    def __str__(self):
        res = ''
        col_sizes = self.allocate()
		# https://stackoverflow.com/a/71309268
