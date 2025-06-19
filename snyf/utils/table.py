import os
import re
from .color import Color

class Link:
    def __init__(self, url):
        self.url = url
        self.text = url

    def __str__(self):
        return f"\033]8;{''};{self.url}\033\\{self.text}\033]8;;\033\\"

    def __len__(self):
        return len(self.text)

    def slice(self, pos, cut=False):
        res = Link(self.url)
        res.text = self.text[:pos]
        if cut:
            self.text = self.text[pos:]

        return res

class Cell:
    def __init__(self, s):
        url_pattern = re.compile(r'(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)')
        self.s = []
        pos = 0
        while True:
            matched = url_pattern.search(s, pos)
            if not matched:
                break

            start, end = matched.span()
            if pos < start:
                self.s.append(s[pos:start])
            self.s.append(Link(s[start:end]))
            pos = end

        self.s.append(s[pos:])

    def __len__(self):
        return sum(map(lambda x: len(x), self.s))

    def clear(self):
        self.s = []
        return self

    def append(self, s):
        self.s.append(s)

    def slice(self, start, end, cut=False):
        # TODO: when I need it lol
        pass

    def slice(self, pos, cut=False):
        cut_len = None
        cur_len = 0
        res = Cell('').clear()
        idx = 0
        while cur_len < pos and idx < len(self.s):
            if cur_len + len(self.s[idx]) <= pos:
                cut_len = None
                res.append(self.s[idx])
                cur_len += len(self.s[idx])
                idx += 1
            else:
                cut_len = pos - cur_len
                if type(self.s[idx]) is Link:
                    res.append(self.s[idx].slice(cut_len, cut))
                else:
                    res.append(self.s[idx][:cut_len])

                cur_len = pos

        if cut:
            self.s = self.s[idx:]
            if cut_len is not None and len(self.s) and type(self.s[0]) is str:
                self.s[0] = self.s[0][cut_len:]

        return res

    def ljust(self, total_len, c):
        if len(c) > 1:
            raise Exception('One character plz')

        pad_len = total_len - len(self)
        return str(self) + c * pad_len

    def __str__(self):
        return ''.join(map(lambda x: str(x), self.s))

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
        self.is_header = []
        self.rows = []
        self.row_formats = []
        self.width = width
        self.format = format.replace('-', '') # wdym u want all cells in a column to be "merged"?
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

    def add_row(self, row, header=False):
        if self.col_num != 0:
            row = row[:self.col_num]
        self.col_cnt = max(self.col_cnt, len(row))
        global_format = self.format.split('|')
        format_idx = 0
        row_format = [''] * len(row)
        for i in range(len(row)):
            row_format[i] = global_format[format_idx]
            if type(row[i]) is tuple:
                row_format[i] += row[i][1]
                merge_cnt = row[i][1].count('-')
                if merge_cnt > 1:
                    format_idx += merge_cnt - 1

                row[i] = row[i][0]

            format_idx += 1

        self.rows.append(list(map(lambda x: Cell(x), row)))
        self.row_formats.append(row_format)
        self.is_header.append(header)

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
        avg_cnt = [0] * self.col_num
        max_len = [0] * self.col_num
        for _ in range(len(self.rows)):
            row = self.rows[_]
            row_format = self.row_formats[_]
            ignore_cnt = 0
            idx = 0
            for i in range(len(row)):
                if i >= self.col_num:
                    break

                # Yep this means fixed columns won't work with
                # merged cells, but who does that anw?
                if '-' in row_format[i]:
                    idx += row_format[i].count('-')
                    continue

                avg_len[idx] += len(row[i])
                avg_cnt[idx] += 1
                max_len[idx] = max(max_len[idx], len(row[i]))
                idx += 1

        for i in range(self.col_num):
            avg_len[i] /= avg_cnt[i]

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
            warn_threshold = self.width // 3
            for i in range(self.col_num):
                if '*' in cols[i]:
                    if not warn_fix and max_len[i] > warn_threshold:
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

    def merged_cells(self, row_format, col_sizes):
        cur_sizes = []

        idx = 0
        merge_cnt = 0
        for size in col_sizes:
            merge_cnt -= 1
            if merge_cnt > 0:
                cur_sizes[-1] += size + 3 # " | "
                continue

            row = row_format[idx]
            if '-' in row:
                merge_cnt = row.count('-')

            cur_sizes.append(size)
            idx += 1

        return cur_sizes

    def __str__(self):
        res = ''
        width, col_sizes = self.allocate()
        # print('Allocation', width, col_sizes)
        hline = '+'
        for size in col_sizes:
            hline += '-' * (size + 2)
            hline += '+'
        hline += '\n'
        header_hline = hline.replace('-', '=')

        res = ''
        res += header_hline if self.is_header[0] else hline
        for idx in range(len(self.rows)):
            row_format = self.row_formats[idx]
            cur_sizes = self.merged_cells(row_format, col_sizes)
            col_num = len(cur_sizes)
            row_format += [''] * (col_num - len(row_format))
            row = self.rows[idx]
            row += [Cell('')] * (col_num - len(row))

            line = ''
            processing = list(map(lambda x: len(x) > 0, row))
            while any(processing) > 0:
                line += '| '
                for i in range(col_num):
                    line += self.__colored(
                        row_format[i],
                        row[i].slice(cur_sizes[i], True).ljust(cur_sizes[i], ' ')
                    )
                    if len(row[i]) == 0:
                        processing[i] = False

                    line += ' | '

                line = line[:-1] + '\n'
            res += line

            if self.is_header[idx] or (idx + 1 < len(self.is_header) and self.is_header[idx + 1]):
                res += header_hline
            else:
                res += hline

        return res
