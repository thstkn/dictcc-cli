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
codes_lines = '\n'.join('  '.join(CODES[ i*CODES_PER_LINE : (i+1)*CODES_PER_LINE ])
                        for i in range(len(CODES) // CODES_PER_LINE + 1))

DEFAULT_LANG1 = 'de'
DEFAULT_LANG2 = 'en'

def select_languages():
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

fromto = f'{DEFAULT_LANG1}{DEFAULT_LANG2}'
if args.language:
    fromto = select_languages()


content = requests.get(f'https://{fromto}.dict.cc/?s={args.word}',
                       headers=Headers().generate()).content
soup = BeautifulSoup(content, 'lxml')
table_elements = soup.find_all('td', class_='td7nl')



def partition_before_thresh(long_str: str, thresh: int, delim: str):
    front, _, _ = long_str[ :thresh ].rpartition(delim)
    back = long_str[ len(front): ]
    return front, back

def split_long_str(long_str: str, thresh: int, delim: str):
    shorten_me = long_str
    tmp_res = ''
    res = None
    FIRST = True
    # this loop is no elegant solution
    for i in range(20):
        dyn_thresh = thresh if FIRST else thresh-2
        # make tuples of positions of spaces
        spaces_before_thresh = tuple(i for i, char
                                     in enumerate(shorten_me[ :dyn_thresh ])
                                     if char == delim)
        spaces_after_thresh = tuple(i for i, char
                                    in enumerate(shorten_me[ dyn_thresh: ])
                                    if char == delim)
        # If there are spaces before thresh, do rpartition up to thresh
        if len(spaces_before_thresh) > 1:
            front, back = partition_before_thresh(shorten_me, thresh, delim)
        # Elif there are spaces after thresh, do partition at earliest
        # possible <SPACE>
        elif len(spaces_after_thresh) >= 0:
            # split pipe symbol from the rest
            front, _, back = shorten_me.partition(delim)
            # split rest at first space
            front2, _, back2 = back.partition(delim)
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
    #msg = f'{res = } not initialized?'
    #assert res, msg
    return res

def preprocess_table(table: List[str]):
    for i, line in enumerate(table):
        if len(line) > COLUMN_WIDTH:
            if max(len(part) for part in line.split(' ')) > COLUMN_WIDTH:
                print(f'Not enough columns in terminal!\n')
            table[i] = split_long_str(line, COLUMN_WIDTH, ' ')
            msg = f'{table[i] = } is not initialized?'
            assert table[i], msg
    return table[:TABLE_LENGTH]

def sift_the_soup():
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
    return preprocess_table(table_left), preprocess_table(table_right)



def longest_table_entry(table):
    longest = 0
    for entry in table:
        try:
            res = max(len(part) for part in entry.split('\n'))
        except:
            res = len(entry)
        longest = res if res > longest else longest
    return longest

def len_place_holders(longest, current):
    return longest - current + 2
def floored_place_holders(longest, current):
    return len_place_holders(longest, current) // 2
def even_place_holders(longest, current):
    return True if len_place_holders(longest, current) % 2 == 0 else False

def left_with_place_holders(left, longest: int):
        length  = len(left)
        left = left if even_place_holders(longest, length) \
                            else f'{left} '
        ph = ' .' * floored_place_holders(longest, length)
        return f'{left} {ph}'


PADDING = '  '
def format_multiline_lines(lsplit, rsplit, longest_l):
    res = ''
    FIRST = True
    SHORT = False
    for i, (l, r) in enumerate(zip_longest(lsplit, rsplit)):
        if l:
            l = l.lstrip()
            if FIRST:
                res += f'{left_with_place_holders(l, longest_l)}{PADDING}'
            elif r:
                res += f'{l}{(longest_l - len(l)) * " "}{PADDING}   '
            else:
                SHORT = True
                break
        else:
            if r:
                res += '\n'.join([f'{(longest_l) * " "}{PADDING}   {r.lstrip()}'
                                  for r in rsplit[ i : ]])
                break
        if r:
            res += f'{r.lstrip()}\n'
        FIRST = False
    # if broken simply add the rest from left as one
    if SHORT:
        res += "\n".join(lsplit[ i :  ])
    return res


def print_table():
    table_left, table_right = sift_the_soup()
    longest_l = longest_table_entry(table_left)
    for i, (left, right) in enumerate(zip(table_left, table_right)):
        if i >= TABLE_LENGTH:
            break
        left = left if left else '<None>'
        lsplit = list(left.split('\n')) if '\n' in left else [left]
        rsplit = list(right.split('\n')) if '\n' in right else [right]

        if len(lsplit) == len(rsplit) == 1:
            lwph = left_with_place_holders(left, longest_l)
            res = f'{lwph}{PADDING}{right}'
        else:
            res = format_multiline_lines(lsplit, rsplit, longest_l)
        print(res)


print_table()

