from shutil import get_terminal_size
from itertools import zip_longest
from dictcc_mini.config import FIELD_STYLES, DEFAULT_STYLE

class TableColumn:
    def __init__(self, entries: list[str],
                 column_width: int, table_length: int, terminal_width: int,
                 field_indicator_style=DEFAULT_STYLE) -> None:
        self.entries = entries
        self.column_width = column_width
        self.table_length = table_length
        self.terminal_width = terminal_width
        self.delim = ' '
        self.longest_other_column: None | int = None
        self.line_width_thresh: None | int = None
        self.field_indicator_style: str = field_indicator_style
        self.verbosity = 'MINIMAL'

    @property
    def field_indicators(self) -> tuple[str, str, str]:
        return FIELD_STYLES[self.field_indicator_style]
    @property
    def stripped_indicators(self) -> tuple[str | None, str | None, str | None]:
        return (stripped if (stripped := ind.strip()) else None
                for ind in self.field_indicators)
    @property
    def longest_entry(self) -> int:
        longest = 0
        for i, entry in enumerate(self.entries):
            if i+1 > self.table_length:
                break
            try:
                res = len(entry) if not '\n' in entry else \
                      max(len(part) for part in entry.split('\n'))
            except Exception as e:
                print(f'exception:\t{e}\n')
            longest = res if res > longest else longest
        return longest

    def get_split_index(self, string: str, start, available_width) -> int:
        split_index = string.rfind(self.delim, start, available_width)
        if split_index == -1:
            split_index = string.find(self.delim, available_width)
            if split_index == -1:
                split_index = available_width
        return split_index

    def get_best_head(self, long_str: str, columns: int) \
            -> tuple[str | None, str | None]:
        split_index = self.get_split_index(long_str, 0, columns)
        head = long_str[ :split_index ].rstrip()
        long_str = long_str[ split_index: ].lstrip()
        return head, long_str

    def partition_to_column(self, long_str: str, columns: int) -> str:
        head, long_str = self.get_best_head(long_str, columns)
        if len(long_str) <= columns:
            return '\n'.join((head, long_str))
        else:
            return '\n'.join((head, self.partition_to_column(long_str, columns)))

    def split_long_str(self, shorten_me: str) -> str | None:
        field_ind0, field_ind1, field_ind2 = self.field_indicators
        lines = []
        is_first_line = True
        while True:
            is_first_line = (len(lines) == 0)
            current_indicator = field_ind0 if is_first_line else field_ind1
            available_width = self.line_width_thresh - len(current_indicator)
            # last line! base condition
            if len(shorten_me) <= available_width:
                break
            # add line and update shorten_me
            head, shorten_me = self.get_best_head(shorten_me, available_width)
            if not head:
                raise ValueError(f'{head = } needs to be assigned here!')
            lines.append(f'{current_indicator}{head}')
        last_indicator = field_ind0 if not lines else field_ind2
        lines.append(f'{last_indicator}{shorten_me}')
        return "\n".join(lines)

    def preprocess(self, longest_other_column: int) -> None:
        self.longest_other_column = longest_other_column
        self.line_width_thresh = self.column_width * 2 - longest_other_column - 2
        entries = self.entries.copy()
        for i, line in enumerate(entries):
            if len(line) > self.line_width_thresh:
                entries[i] = self.split_long_str(line)
                if not entries[i]:
                    msg = f'{entries[i] = } is not initialized?\n{line}'
                    raise ValueError(msg)
            if i+1 >= self.table_length:
                break
        self.entries = entries

class Table:
    def __init__(self, entries_left, entries_right, full_table,
                 verbosity: str = 'MINIMAL') -> None:
        self.table_length = 20 if not full_table else 1000
        terminal_width = get_terminal_size()[0]
        self.column_width = (terminal_width - 2) // 2
        self.pad_right_of_placeholders = ''
        self.pad_left_of_placeholders = ''
        self.verbosity = verbosity
        CENTER_MARGIN = 3

        left_column = TableColumn(entries_left, self.column_width,
                                  self.table_length, terminal_width)
        right_column = TableColumn(entries_right, self.column_width,
                                   self.table_length, terminal_width)

        if any(len(left) + len(right) + CENTER_MARGIN >= terminal_width
               for left in left_column.entries
               for right in right_column.entries):

            rlong = right_column.longest_entry
            longest_right = rlong if rlong <= self.column_width else self.column_width

            if verbosity == 'DEBUG':
                print(f'{rlong = }\n{longest_right = }\n')
            left_column.preprocess(longest_right)
            llong = left_column.longest_entry
            longest_left = llong if llong <= self.column_width else self.column_width

            if verbosity == 'DEBUG':
                print(f'{llong = }\n{longest_left = }\n')
            right_column.preprocess(longest_left)

        SUM = left_column.longest_entry + right_column.longest_entry + CENTER_MARGIN
        if SUM > terminal_width:
            msg = f'Terminal very small: {terminal_width} columns. ' \
                  f'Expect tearing.\n'
            print(self.partition_to_column(msg, columns=terminal_width))

        self.left_column, self.right_column = left_column, right_column
        # this can only be determined after preprocessing, as it depends on
        # where lines have been broken.
        self.longest_l = left_column.longest_entry

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

    def format_multiline_entries(self, lsplit, rsplit) -> str:
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
            # if entries havent been broken take this shortcut
            if len(lsplit) == len(rsplit) == 1:
                res += f'{self.left_with_place_holders(left)}{right}\n'
            else:
                res += f'{self.format_multiline_entries(lsplit, rsplit)}\n'
        print(res.rstrip())
