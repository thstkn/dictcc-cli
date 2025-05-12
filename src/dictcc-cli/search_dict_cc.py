from typing import Optional
from shutil import get_terminal_size
import requests
from itertools import zip_longest
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from fake_headers import Headers

def parse():
    parser = ArgumentParser(prog='dict.cc-cli',
                            description='I like trains.',
                            epilog='Nice.')
    parser.add_argument('word', type=str, help='lookup this word')
    parser.add_argument('-f', '--full', action='store_true', required=False,
                        help="don't shorten to 20 entries")
    parser.add_argument('-l', '--language', action='store_true', required=False,
                        help='start with language selector')
    return parser.parse_args()
ARGS = parse()

TABLE_LENGTH = 20 if not ARGS.full else 1000
COLUMN_WIDTH = (get_terminal_size()[0] - 5) // 2

CODES = ['EN', 'SV', 'IS', 'RU', 'RO', 'FR', 'IT', 'SK', 'NL', 'PT', 'LA', 'FI',
         'ES', 'HU', 'NO', 'BG', 'HR', 'CS', 'DA', 'TR', 'UK', 'PL', 'EO', 'SR',
         'SQ', 'EL', 'BS', 'DE']
CODES = list(sorted(CODES))
CODES_PER_LINE = (COLUMN_WIDTH * 2 + 5) // 4

DEFAULT_LANG1, DEFAULT_LANG2 = 'de', 'en'

def select_languages() -> str:
    country_codes = '\n'.join('  '.join(CODES[ i*CODES_PER_LINE : (i+1)*CODES_PER_LINE ])
                              for i in range(len(CODES) // CODES_PER_LINE + 1))
    print(f'{country_codes}')
    user_inputs = ['', '']
    FIRST = True
    while not all(i.upper() in CODES for i in user_inputs):
        prompt = f'Enter two country codes: ' if FIRST else \
                 f'Enter two space-separated country codes: '
        FIRST = False
        try:
            in1, in2 = input(prompt).split()
        except Exception as e:
            continue
        user_inputs = [in1, in2]
        for i, user_input in enumerate(user_inputs):
            if user_input.upper() not in CODES:
                if i >= 1 and user_input == '':
                    print(f"Defaulting to '{DEFAULT_LANG1.upper()}'\n")
                    user_inputs[1] = DEFAULT_LANG1
                else:
                    print(f'Invalid language selector: {user_input}')
    return ''.join(user_inputs)

def sift_the_soup(content) -> tuple[list[str], list[str]]:
    soup = BeautifulSoup(content, 'lxml')
    table_elements = soup.find_all('td', class_='td7nl')
    table_left = []
    table_right = []
    for i in range(0, len(table_elements), 2):
        l = table_elements[i]
        r = table_elements[i+1]
        table_left.append(' '.join(ref.text for ref in l.find_all(['a'])))
        table_right.append(' '.join(ref.text for ref in r.find_all(['a'])))
# dfns are optional chunks of information in brackets on dict.cc which differ
# from those brackets which are contained in the strings from a-refs above and
# need to be added extra like below
        dfns_l = l.find_all(['dfn'])
        dfns_r = r.find_all(['dfn'])
        if dfns_l:
            table_left[-1] += ' ' + ' '.join(f'[{d.text}]' for d in dfns_l)
        if dfns_r:
            table_right[-1] += ' ' + ' '.join(f'[{d.text}]' for d in dfns_r)
    return table_left, table_right

fromto = f'{DEFAULT_LANG1}{DEFAULT_LANG2}'
if ARGS.language:
    fromto = select_languages()
    print()
CONTENT = requests.get(url=f'https://{fromto}.dict.cc/?s={ARGS.word}',
                       headers=Headers().generate()).content

class TableColumn:
    def __init__(self, entries: list[str],
                 column_width: int, table_length: int) -> None:
        self.entries = entries
        self.column_width = column_width
        self.table_length = table_length
        self.delim = ' '

    def partition_before_thresh(self, long_str: str,
                                longest_other_column: int) -> tuple[str, str]:
        thresh = self.column_width * 2 - longest_other_column
        front, _, _ = long_str[ : thresh ].rpartition(self.delim)
        back = long_str[ len(front): ]
        return front, back

    def partition_after_thresh(self, long_str: str) -> tuple[str, str]:
        # split pipe symbol from the rest
        front, _, back = long_str.partition(self.delim)
        # split rest at first space
        front2, _, back2 = back.partition(self.delim)
        return f'{front} {front2}', back2

    def split_long_str(self, shorten_me: str,
                       longest_other_column: int) -> Optional[str]:
        dyn_thresh = 2 * self.column_width - longest_other_column
        tmp_res = ''
        res = None
        FIRST = True
        back = None
        # this loop is no elegant solution
        for _ in range(20):
            dyn_thresh = dyn_thresh if FIRST else dyn_thresh - 2
            # make tuples of positions of spaces
            delims_before_thresh = tuple(i for i, char
                                         in enumerate(shorten_me[ : dyn_thresh ])
                                         if char == self.delim)
            delims_after_thresh = tuple(i for i, char
                                        in enumerate(shorten_me[ dyn_thresh : ])
                                        if char == self.delim)
            # If there are spaces before thresh, do rpartition up to thresh
            if len(delims_before_thresh) > 1:
                front, back = self.partition_before_thresh(shorten_me,
                                                           longest_other_column)
            # Elif there are delim after thresh, do partition at earliest
            # possible <delim>
            elif len(delims_after_thresh) >= 0:
                front, back = self.partition_after_thresh(shorten_me)
            if not back:
                return res
            back = back.lstrip()
            if len(back) <= dyn_thresh:
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
        entries = self.entries.copy()
        for i, line in enumerate(entries):
            if len(line) > self.column_width * 2 - longest_other_column:
                #if any(len(part) for part in line.split(' ')) > self.column_width:
                    #print(f'Not enough columns in terminal!\n')
                entries[i] = self.split_long_str(line, longest_other_column)
                #msg = f'{entries[i] = } is not initialized?'
                #assert entries[i], msg
                if not entries[i]:
                    return False
        self.entries = entries[ : self.table_length]
        return True

    def longest_entry(self) -> int:
        longest = 0
        for entry in self.entries:
            try:
                res = max(len(part) for part in entry.split('\n'))
            except:
                res = len(entry)
            longest = res if res > longest else longest
        return longest

class Table:
    def __init__(self, column_width, table_length) -> None:
        entries_left, entries_right = sift_the_soup(CONTENT)
        self.left_column = TableColumn(entries_left, column_width, table_length)
        self.right_column = TableColumn(entries_right, column_width, table_length)
        if not self.left_column.entries:
            print('No result')
            return
        self.column_width = column_width
        self.table_length = table_length
        self.padding = '  '
        # only preprocess if needed
        ABORT = False
        if any(len(left) + len(right) + 5 >= get_terminal_size()[0]
               for left in self.left_column.entries
               for right in self.right_column.entries):
            msg = f'Terminal too small? Only {get_terminal_size()[0]} columns!\n'
            rlong = self.right_column.longest_entry()
            longest_right = rlong if rlong <= self.column_width else self.column_width
            if not self.left_column.preprocess(longest_right):
                ABORT = True
            llong = self.left_column.longest_entry()
            longest_left = llong if llong <= self.column_width else self.column_width
            if not self.right_column.preprocess(longest_left):
                ABORT = True
            if ABORT:
                print(msg)
        # this can only be determined after preprocessing, as it depends on
        # where lines have been broken.
        self.longest_l = self.left_column.longest_entry()

    def len_place_holders(self, left) -> int:
        return self.longest_l - len(left) + 2
    def floored_place_holders(self, left) -> int:
        return self.len_place_holders(left) // 2
    def even_place_holders(self, left) -> bool:
        return True if self.len_place_holders(left) % 2 == 0 else False
    def left_with_place_holders(self, left) -> str:
            left = left if self.even_place_holders(left) else f'{left} '
            return f'{left} {' .' * self.floored_place_holders(left)}'

    def format_multiline_lines(self, lsplit, rsplit) -> str:
        FIRST = True
        res = ''
        for i, (l, r) in enumerate(zip_longest(lsplit, rsplit)):
            if l:
                if FIRST:
                    FIRST = False
                    res += f'{self.left_with_place_holders(l)}{self.padding}'
                elif r:
                    FIRST = False
                    res += f'{l}{(self.longest_l - len(l)) * " "}{self.padding}   '
                else:
                    FIRST = False
                    # if no further r lines found simply add the rest from left as one
                    res += "\n".join(lsplit[ i :  ])
                    break
            else:
                if r:
                    # if no further l lines found simply add the rest from right as one
                    res += '\n'.join([f'{(self.longest_l) * " "}{self.padding}   {r}'
                                      for r in rsplit[ i : ]])
                    break
            if r:
                res += f'{r}\n'
            #FIRST = False
        return res.rstrip()     # remove excessive new lines with rstrip

    def show(self) -> None:
        for i, (left, right) in enumerate(zip(self.left_column.entries, self.right_column.entries)):
            if i >= self.table_length:
                break
            lsplit = list(left.split('\n')) if '\n' in left else [left]
            rsplit = list(right.split('\n')) if '\n' in right else [right]
            lsplit = [l.lstrip() for l in lsplit]
            rsplit = [r.lstrip() for r in rsplit]
            # if entries havent been broken take this shortcut
            if len(lsplit) == len(rsplit) == 1:
                res = f'{self.left_with_place_holders(left)}{self.padding}{right}'
            else:
                res = self.format_multiline_lines(lsplit, rsplit)
            #res = res if res.isspace() else "No result"
            print(res)


table = Table(COLUMN_WIDTH, TABLE_LENGTH)
table.show()

