from shutil import get_terminal_size
from itertools import zip_longest
from typing import Optional

class TableColumn:
    def __init__(self, entries: list[str],
                 column_width: int, table_length: int) -> None:
        self.entries = entries
        self.column_width = column_width
        self.table_length = table_length
        self.delim = ' '
        self.longest_other_column: None | int = None
        self.line_width_thresh: None | int = None

    def partition_before_thresh(self, long_str: str) -> tuple[str, str]:
        front, _, _ = long_str[ : self.line_width_thresh ].rpartition(self.delim)
        back = long_str[ len(front): ]
        return front, back

    def partition_after_thresh(self, long_str: str) -> tuple[str, str]:
        # split pipe symbol from the rest
        front, _, back = long_str.partition(self.delim)
        # split rest at first space
        front2, _, back2 = back.partition(self.delim)
        return f'{front} {front2}', back2

    def split_long_str(self, shorten_me: str) -> Optional[str]:
        tmp_res = ''
        res = None
        FIRST = True
        back = None
        # this loop is no elegant solution - enough for 33 line breaks
        for _ in range(len(shorten_me)):
            self.line_width_thresh = self.line_width_thresh if FIRST \
                                     else self.line_width_thresh - 2
            # make tuples of positions of spaces
            delims_before_thresh = \
                    tuple(i for i, char
                          in enumerate(shorten_me[ : self.line_width_thresh ])
                          if char == self.delim)
            delims_after_thresh = \
                    tuple(i for i, char
                          in enumerate(shorten_me[ self.line_width_thresh : ])
                          if char == self.delim)
            # If there are spaces before thresh, do rpartition up to thresh
            if len(delims_before_thresh) > 1:
                front, back = self.partition_before_thresh(shorten_me)
            # Elif there are delim after thresh, do partition at earliest
            # possible <delim>
            elif len(delims_after_thresh) >= 0:
                front, back = self.partition_after_thresh(shorten_me)
            if not back:
                return res
            back = back.lstrip()
            if len(back) <= self.line_width_thresh:
                if FIRST:
                    if back:
                        res = f'{front}\n╰╴{back}'
                    else:
                        res = front
                    break
                else:
                    res = f'{tmp_res}\n{front}\n╰╴{back}'
                    break
            else:
                back = f'│ {back}'
                if FIRST:
                    tmp_res = front
                else:
                    tmp_res = f'{tmp_res}\n{front}'
            shorten_me = back
            FIRST = False
        return res

    def preprocess(self, longest_other_column: int) -> bool:
        self.longest_other_column = longest_other_column
        self.line_width_thresh = self.column_width * 2 - longest_other_column
        entries = self.entries.copy()
        for i, line in enumerate(entries):
            if len(line) > self.line_width_thresh:
                #if any(len(part) for part in line.split(' ')) > self.column_width:
                    #print(f'Not enough columns in terminal!\n')
                entries[i] = self.split_long_str(line)
                #msg = f'{entries[i] = } is not initialized?'
                #assert entries[i], msg
                if not entries[i]:
                    return False
            if i+1 >= self.table_length:
                break
        self.entries = entries
        return True

    def longest_entry(self) -> int:
        longest = 0
        for i, entry in enumerate(self.entries):
            if i+1 > self.table_length:
                break
            res = len(entry) if not '\n' in entry else \
                  max(len(part) for part in entry.split('\n'))
            longest = res if res > longest else longest
        return longest

class Table:
    def __init__(self, entries_left, entries_right, full_table) -> None:
        self.table_length = 20 if not full_table else 1000
        terminal_width = get_terminal_size()[0]
        self.column_width = (terminal_width - 2) // 2
        self.pad_right_of_placeholders = ''
        self.pad_left_of_placeholders = ''

        left_column = TableColumn(entries_left, self.column_width, self.table_length)
        right_column = TableColumn(entries_right, self.column_width, self.table_length)

        TOO_SMALL = False
        if any(len(left) + len(right) + 3 >= terminal_width
               for left in left_column.entries
               for right in right_column.entries):
            rlong = right_column.longest_entry()
            longest_right = rlong if rlong <= self.column_width else self.column_width
            if not left_column.preprocess(longest_right):
                TOO_SMALL = True
            llong = left_column.longest_entry()
            longest_left = llong if llong <= self.column_width else self.column_width
            if not right_column.preprocess(longest_left):
                TOO_SMALL = True
            if TOO_SMALL:
                print(f'Terminal too small? Only {terminal_width} columns!\n')
        self.left_column, self.right_column = left_column, right_column
        # this can only be determined after preprocessing, as it depends on
        # where lines have been broken.
        self.longest_l = left_column.longest_entry()

    def len_place_holders(self, left) -> int:
        return self.longest_l - len(left)

    def left_with_place_holders(self, left, first: bool = True) -> str:
        self.inline_pad = ' . ' if first else '   '
        # evens out dotted lines on the left edge
        rest = self.len_place_holders(left) % len(self.inline_pad)
        left = f'{left}{' ' * rest}'
        how_many_pads = self.len_place_holders(left) // len(self.inline_pad) + 1
        place_holders = self.inline_pad * how_many_pads
        return f'{left}{self.pad_left_of_placeholders}' \
               f'{place_holders}{self.pad_right_of_placeholders}'

    def format_multiline_lines(self, lsplit, rsplit) -> str:
        FIRST = True
        res = ''
        for i, (l, r) in enumerate(zip_longest(lsplit, rsplit)):
            if l:
                if FIRST:
                    FIRST = False
                    res += f'{self.left_with_place_holders(l)}'
                elif r:     # compensate for no lineup self.inline_pad on consecutive lines
                    res += f'{self.left_with_place_holders(l, first = False)}'
                else:       # if no further r lines found add the rest from left as one
                    res += "\n".join(lsplit[ i :  ])
                    break
            else:   # if no further l lines found add the rest from right as one
                if r:
                    left_pad_factor = self.longest_l + len(self.inline_pad)
                    l_pad_str = f'{left_pad_factor * ' '}' \
                                f'{self.pad_left_of_placeholders}' \
                                f'{self.pad_right_of_placeholders}'
                    res += '\n'.join([f'{l_pad_str}{r}' for r in rsplit[ i : ]])
                    break
            if r:           # add right side after prep above
                res += f'{r}\n'
        return res.rstrip()     # remove excessive new lines with rstrip

    def show(self) -> None:
        res = ''
        for i, (left, right) in enumerate(zip(self.left_column.entries,
                                              self.right_column.entries)):
            if i >= self.table_length:
                break
            lsplit = list(left.split('\n')) if '\n' in left else [left]
            rsplit = list(right.split('\n')) if '\n' in right else [right]
            lsplit, rsplit = [l.lstrip() for l in lsplit], [r.lstrip() for r in rsplit]
            # if entries havent been broken take this shortcut
            if len(lsplit) == len(rsplit) == 1:
                res += f'{self.left_with_place_holders(left)}{right}\n'
            else:
                res += f'{self.format_multiline_lines(lsplit, rsplit)}\n'
        print(res.rstrip())
