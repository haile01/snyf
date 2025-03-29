import os

class Table:
    def __init__(self, format = "", col_num = 0, width = os.get_terminal_size()[0]):
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
        self.rows = []
        self.width = width
        self.format = format
        self.col_num = col_num
        self.col_cnt = 0
        self.header = False

    def colored(self, color, text):
        return self.colors[color] + text + self.colors['end']

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)

    def add_row(self, row):
        self.col_cnt = max(self.col_cnt, len(row))
        self.rows.append(row)

    def allocate(self):
        # TODO: test this throughoutly
        # NOTE:
        # 1. If there exist fixed row, they must stand on one line
        # 2. If total width exceeds the CLI size, bail
        # 3. Take the average of line lengths, not maximum

        if self.format != "":
            cols = self.format.split('|')
            col_num = len(cols)
        elif self.col_num != 0:
            col_num = self.col_num
        else:
            col_num = max(list(map(lambda r: len(r), self.rows)))

        avg_len = [0] * col_num
        max_len = [0] * col_num
        for row in self.rows:
            for i in range(len(row)):
                avg_len[i] += len(row[i])
                max_len[i] = max(max_len[i], len(row[i]))

        for i in range(col_num):
            avg_len[i] /= len(row)

        # | ... | ... | ... |
        avail_len = self.width - (3 * (col_num + 1) - 2)
        if self.format == "":
            # In case stuffs r too small
            if sum(max_len) < avail_len:
                return (self.width - avail_len + sum(max_len)), max_len

            base = sum(avg_len)
            res = []
            for i in range(col_num - 1):
                res.append(int(avg_len[i] * avail_len / base))
            res.append(avail_len - sum(res))
            return self.width, res
        else:
            res = [0] * col_num
            base = 0
            non_fixed = []
            warn_fix = False
            for i in range(col_num):
                if len(cols[i]) and cols[i][0] == '*':
                    if not warn_fix and max_len[i] > 10:
                        print(self.colored('bold', "Warning: text is a bit long for a fixed column..."))
                        warn_fix = True

                    res[i] = max_len[i]

                else:
                    base += avg_len[i]
                    non_fixed.append(i)

            tmp_len = avail_len - sum(res)
            if tmp_len < 0:
                print(self.colored('bold', "Text line too long, I ain't print it bro..."))
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
        for row in self.rows:
            line = ''
            processing = list(map(lambda x: len(x) > 0, row))
            while any(processing) > 0:
                line += '| '
                for i in range(len(col_sizes)):
                    line += row[i][:col_sizes[i]].ljust(col_sizes[i], ' ')
                    row[i] = row[i][col_sizes[i]:]
                    if row[i] == '':
                        processing[i] = False

                    line += ' | '

                line = line[:-1] + '\n'
            res += line
            res += hline

        return res
