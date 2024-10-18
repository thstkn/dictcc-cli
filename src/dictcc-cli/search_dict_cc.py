#!/bin/python3.13

from typing import List
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
args = parse()


TABLE_LENGTH = 20 if not args.full else 1000
COLUMN_WIDTH = (get_terminal_size()[0] - 5) // 2

CODES = ['EN', 'SV', 'IS', 'RU', 'RO', 'FR', 'IT', 'SK', 'NL', 'PT', 'LA', 'FI',
         'ES', 'HU', 'NO', 'BG', 'HR', 'CS', 'DA', 'TR', 'UK', 'PL', 'EO', 'SR',
         'SQ', 'EL', 'BS', 'DE']
CODES = list(sorted(CODES))
CODES_PER_LINE = (COLUMN_WIDTH * 2 + 5) // 4

DEFAULT_LANG1 = 'de'
DEFAULT_LANG2 = 'en'

def select_languages():
    codes_lines = '\n'.join('  '.join(CODES[ i*CODES_PER_LINE : (i+1)*CODES_PER_LINE ])
                            for i in range(len(CODES) // CODES_PER_LINE + 1))
    user_inputs = ['', '']
    while not all(i.upper() in CODES for i in user_inputs):
        prompt = f'Enter 2 of the following country codes:\n{codes_lines}\n1: '
        user_inputs = [input(prompt), input('2: ')]
        for i, user_input in enumerate(user_inputs):
            if user_input.upper() not in CODES:
                if i >= 1 and user_input == '':
                    print(f"Defaulting to '{DEFAULT_LANG1.upper()}'\n")
                    user_inputs[1] = DEFAULT_LANG1
                else:
                    print(f'Invalid language selector: {user_input}')
    return ''.join(user_inputs)

def sift_the_soup(content):
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

class TableColumn:
    def __init__(self, entries: List[str],
                 column_width: int, table_length: int) -> None:
        self.column_width = column_width
        self.table_length = table_length
        self.delim = ' '
        self.entries = self.preprocess(entries)

    def partition_before_thresh(self, long_str: str):
        front, _, _ = long_str[ : self.column_width ].rpartition(self.delim)
        back = long_str[ len(front): ]
        return front, back

    def split_long_str(self, long_str: str):
        shorten_me = long_str
        tmp_res = ''
        res = None
        FIRST = True
        # this loop is no elegant solution
        for i in range(20):
            dyn_thresh = self.column_width if FIRST else self.column_width-2
            # make tuples of positions of spaces
            spaces_before_thresh = tuple(i for i, char
                                         in enumerate(shorten_me[ :dyn_thresh ])
                                         if char == self.delim)
            spaces_after_thresh = tuple(i for i, char
                                        in enumerate(shorten_me[ dyn_thresh: ])
                                        if char == self.delim)
            # If there are spaces before thresh, do rpartition up to thresh
            if len(spaces_before_thresh) > 1:
                front, back = self.partition_before_thresh(shorten_me)
            # Elif there are spaces after thresh, do partition at earliest
            # possible <SPACE>
            elif len(spaces_after_thresh) >= 0:
                # split pipe symbol from the rest
                front, _, back = shorten_me.partition(self.delim)
                # split rest at first space
                front2, _, back2 = back.partition(self.delim)
                front = f'{front} {front2}'
                back = back2
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

    def preprocess(self, entries: List[str]):
        for i, line in enumerate(entries):
            if len(line) > self.column_width:
                if max(len(part) for part in line.split(' ')) > self.column_width:
                    print(f'Not enough columns in terminal!\n')
                entries[i] = self.split_long_str(line)
                msg = f'{entries[i] = } is not initialized?'
                assert entries[i], msg
        return entries[ : self.table_length]

    def longest_entry(self):
        longest = 0
        for entry in self.entries:
            try:
                res = max(len(part) for part in entry.split('\n'))
            except:
                res = len(entry)
            longest = res if res > longest else longest
        return longest

class Table:
    def __init__(self, table_left, table_right,
                 column_width, table_length) -> None:
        self.left_column = TableColumn(table_left, column_width, table_length)
        self.right_column = TableColumn(table_right, column_width, table_length)
        self.column_width = column_width
        self.table_length = table_length
        self.longest_l = self.left_column.longest_entry()
        self.padding = '  '

    def len_place_holders(self, left):
        return self.longest_l - len(left) + 2
    def floored_place_holders(self, left):
        return self.len_place_holders(left) // 2
    def even_place_holders(self, left):
        return True if self.len_place_holders(left) % 2 == 0 else False
    def left_with_place_holders(self, left):
            left = left if self.even_place_holders(left) else f'{left} '
            ph = ' .' * self.floored_place_holders(left)
            return f'{left} {ph}'

    def format_multiline_lines(self, lsplit, rsplit):
        FIRST = True
        SHORT = False
        res = ''
        for i, (l, r) in enumerate(zip_longest(lsplit, rsplit)):
            if l:
                l = l.lstrip()
                if FIRST:
                    res += f'{self.left_with_place_holders(l)}{self.padding}'
                elif r:
                    res += f'{l}{(self.longest_l - len(l)) * " "}{self.padding}   '
                else:
                    SHORT = True
                    break
            else:
                if r:
                    res += '\n'.join([f'{(self.longest_l) * " "}{self.padding}   {r.lstrip()}'
                                      for r in rsplit[ i : ]])
                    break
            if r:
                res += f'{r.lstrip()}\n'
            FIRST = False
        # if broken simply add the rest from left as one
        if SHORT:
            res += "\n".join(lsplit[ i :  ])
        return res

    def print(self):
        for i, (left, right) in enumerate(zip(self.left_column.entries, self.right_column.entries)):
            if i >= self.table_length:
                break
            left = left if left else '<None>'
            lsplit = list(left.split('\n')) if '\n' in left else [left]
            rsplit = list(right.split('\n')) if '\n' in right else [right]

            if len(lsplit) == len(rsplit) == 1:
                lwph = self.left_with_place_holders(left)
                res = f'{lwph}{self.padding}{right}'
            else:
                res = self.format_multiline_lines(lsplit, rsplit)
            print(res)


fromto = f'{DEFAULT_LANG1}{DEFAULT_LANG2}'
if args.language:
    fromto = select_languages()

content = requests.get(url=f'https://{fromto}.dict.cc/?s={args.word}',
                       headers=Headers().generate()).content

entries_left, entries_right = sift_the_soup(content)

table = Table(entries_left, entries_right, COLUMN_WIDTH, TABLE_LENGTH)
table.print()

