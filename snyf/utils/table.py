import os
from .color import Color

class Table:
    def __init__(self, format = "", col_num = 0, width = os.get_terminal_size()[0]):
        self.colors = {
            '': Color(''),
            'h': Color('\033[95m'), # header
            'p': Color('\033[94m'), # primary
            'i': Color('\033[96m'), # info
            's': Color('\033[92m'), # success
            'w': Color('\033[93m'), # warning
            'e': Color('\033[91m'), # error
            'b': Color('\033[1m'),  # bold
            'u': Color('\033[4m')   # underline
        }
        self.rows = []
        self.row_formats = []
        self.width = width
        self.format = format
        # NOTE: col_cnt is the actual data
        #       col_num is fixed in initialization
        self.col_cnt = 0
        self.col_num = len(format.split('|')) if format != '' else col_num
        self.header = False

    def __colored(self, color, text):
        res = text
        for c in list(color):
            if c in self.colors:
                res = self.colors[c].p(res)

        return res

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)

    def add_row(self, row):
        if self.col_num != 0:
            row = row[:self.col_num]
        self.col_cnt = max(self.col_cnt, len(row))
        row_format = self.format.split('|')
        for i in range(len(row)):
            if type(row[i]) is str:
                if len(row_format) <= i:
                    row_format.append('')
            elif type(row[i]) is tuple:
                if len(row_format) <= i:
                    row_format.append(row[i][1])
                else:
                    row_format[i] += row[i][1]
                row[i] = row[i][0]

        self.rows.append(row)
        self.row_formats.append(row_format)

    def allocate(self):
        # TODO: test this throughoutly
        # NOTE:
        # 1. If there exist fixed row, they must stand on one line
        # 2. If total width exceeds the CLI size, bail
        # 3. Distribute based on the average
        #    of line lengths, not maximum

        if self.format != "":
            cols = self.format.split('|')

        if self.col_num == 0:
            self.col_num = self.col_cnt

        avg_len = [0] * self.col_num
        max_len = [0] * self.col_num
        for row in self.rows:
            for i in range(len(row)):
                if i >= self.col_num:
                    break

                avg_len[i] += len(row[i])
                max_len[i] = max(max_len[i], len(row[i]))

        # | ... | ... | ... |
        avail_len = self.width - (3 * (self.col_num + 1) - 2)
        if '*' not in self.format:
            # In case stuffs r too small
            if sum(max_len) < avail_len:
                return (self.width - avail_len + sum(max_len)), max_len

            base = sum(avg_len)
            res = []
            for i in range(self.col_num - 1):
                res.append(int(avg_len[i] * avail_len / base))
            res.append(avail_len - sum(res))
            return self.width, res
        else:
            res = [0] * self.col_num
            base = 0
            non_fixed = []
            warn_fix = False
            for i in range(self.col_num):
                if '*' in cols[i]:
                    if not warn_fix and max_len[i] > 10:
                        print(self.__colored('b', "Warning: text is a bit long for a fixed column..."))
                        warn_fix = True

                    res[i] = max_len[i]

                else:
                    base += avg_len[i]
                    non_fixed.append(i)

            tmp_len = avail_len - sum(res)
            if tmp_len < 0:
                print(self.__colored('b', "Text line too long, I ain't print it bro..."))
                raise Exception("Fixed column is too long")

            for i in range(len(non_fixed) - 1):
                idx = non_fixed[i]
                res[idx] = int(avg_len[idx] * tmp_len / base)

            res[non_fixed[-1]] = avail_len - sum(res)
            return self.width, res

    def __str__(self):
        res = ''
        width, col_sizes = self.allocate()
        print('Allocation', width, col_sizes)
		# https://stackoverflow.com/a/71309268
        hline = '+'
        for size in col_sizes:
            hline += '-' * (size + 2)
            hline += '+'
        hline += '\n'

        res = ''
        res += hline
        for _ in range(len(self.rows)):
            row = self.rows[_]
            row += [''] * (self.col_num - len(row))
            row_format = self.row_formats[_]
            row_format += [''] * (self.col_num - len(row_format))
            line = ''
            processing = list(map(lambda x: len(x) > 0, row))
            while any(processing) > 0:
                line += '| '
                for i in range(self.col_num):
                    line += self.__colored(
                        row_format[i],
                        row[i][:col_sizes[i]].ljust(col_sizes[i], ' ')
                    )
                    row[i] = row[i][col_sizes[i]:]
                    if row[i] == '':
                        processing[i] = False

                    line += ' | '

                line = line[:-1] + '\n'
            res += line
            res += hline

        return res
