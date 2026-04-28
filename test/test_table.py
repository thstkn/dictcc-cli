#!/usr/bin/python3.15

import json
from dictcc_mini.table import Table
from os.path import join
from os import listdir, getenv

#WIDTHS = [80, 40, 30, 20]
WIDTHS = [80, 20]
dictmini_path = getenv('DICTCC_BASE', None)
assert dictmini_path, 'Make sure `DICTCC_BASE` env var is set to correct path'
PATH = f'{dictmini_path}/test/data'
PATHS = [join(PATH, l) for l in listdir(PATH) if 'json' in l]

def test_rendering_logic(path: str):
    print(f'\nTesting:\t{path}')
    with open(path, "r") as f:
        data = json.load(f)

    for width in WIDTHS:
        print(f"width:\t\t{width}\tword:\t{data['word']}")
        table = Table(data['left'],
                      data['right'],
                      full_table=False,
                      terminal_width=width)
        table.show()

if __name__ == '__main__':
    for path in PATHS:
        test_rendering_logic(path)
