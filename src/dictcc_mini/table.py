from shutil import get_terminal_size
from itertools import zip_longest
from dictcc_mini.config import FIELD_STYLES, FIELD_DEFAULT, \
                               INLINE_STYLES, INLINE_DEFAULT
from dictcc_mini.misc import partition_to_column, next_head

class TableColumn:
    def __init__(self, entries: list[str],
                 terminal_width: int, column_width: int, table_length: int,
                 center_margin: int,
                 field_indicator_style=FIELD_DEFAULT,) -> None:
        self.entries = entries
        self.terminal_width = terminal_width
        self.column_width = column_width
        self.table_length = table_length
        self.center_margin = center_margin
        self.delim = ' '
        self.longest_other_column: None | int = None
        self.line_width_thresh: None | int = None
        self.field_indicator_style: str = field_indicator_style

    @property
    def field_indicators(self) -> tuple[str, str, str]:
        return FIELD_STYLES[self.field_indicator_style]
    @property
    def stripped_indicators(self) -> tuple[str | None, ...]:
        return tuple(stripped if (stripped := ind.strip()) else None
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
                break       # add line and update shorten_me
            head, shorten_me = next_head(shorten_me, available_width)
            if not head:
                raise ValueError(f'{head = } needs to be assigned here!')
            lines.append(f'{current_indicator}{head}')
        last_indicator = field_ind0 if not lines else field_ind2
        lines.append(f'{last_indicator}{shorten_me}')
        return "\n".join(lines)

    def preprocess(self, longest_other_column: int) -> None:
        self.longest_other_column = longest_other_column
        self.line_width_thresh = self.terminal_width - longest_other_column - self.center_margin
        #print(f'{self.terminal_width = }\n{longest_other_column = }\n{self.line_width_thresh = }')
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
                 terminal_width: None | int = None) -> None:
        self.table_length = 20 if not full_table else 1000
        terminal_width = get_terminal_size()[0] if not terminal_width else \
                         terminal_width
        self.column_width = (terminal_width - 2) // 2
        self.pad_right_of_placeholders = ''
        self.pad_left_of_placeholders = ''
        CENTER_MARGIN = len(INLINE_DEFAULT[0])
        l_col = TableColumn(
                entries_left, terminal_width, self.column_width,
                self.table_length, center_margin=CENTER_MARGIN)
        r_col = TableColumn(
                entries_right, terminal_width, self.column_width,
                self.table_length, center_margin=CENTER_MARGIN)
        self.left_column, self.right_column = self.negotiate_widths(
                l_col, r_col, terminal_width, CENTER_MARGIN)
        SUM = self.left_column.longest_entry + \
              self.right_column.longest_entry + CENTER_MARGIN
        if SUM > terminal_width:
            msg = f'Terminal very small: {terminal_width} columns. ' \
                  f'Expect tearing.'
            print(f'{partition_to_column(msg, terminal_width)}\n')
        # this can only be determined after negotiate_widths as it
        # depends on where lines have been broken.
        self.longest_l = self.left_column.longest_entry

    def negotiate_widths(self, left_column: TableColumn,
                         right_column: TableColumn,
                         terminal_width: int, margin: int) \
                                 -> tuple[TableColumn, TableColumn]:
        max_l, max_r = (col.longest_entry for col in (left_column, right_column))
        available_total = terminal_width - margin
        if max_l + max_r <= available_total:
            return left_column, right_column

        fair_share = available_total // 2

        if max_l <= fair_share:
            target_l, target_r = max_l, available_total - max_l
        if max_r <= fair_share:
            target_l, target_r = available_total - max_r, max_r
        target_l = fair_share
        target_r = available_total - fair_share
        left_column.preprocess(target_l)
        right_column.preprocess(target_r)
        return left_column, right_column

    def len_place_holders(self, left) -> int:
        return self.longest_l - len(left)

    def left_with_place_holders(self, left, first: bool = True) -> str:
        pad = INLINE_STYLES[INLINE_DEFAULT]
        self.inline_pad = pad[0] if first else pad[1]
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
