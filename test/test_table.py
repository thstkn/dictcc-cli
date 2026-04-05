#!/usr/bin/python3.15

import json
from dictcc_mini.table import Table
from os.path import join
from os import listdir

WIDTHS = [80, 40, 30, 20]
PATH = "/home/lnrd/git/_thstkn/dictcc-mini/test/data"
PATHS = [join(PATH, l) for l in listdir(PATH)]

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
        # Manually override the width if your class supports it
        # table.column_width = (width - 2) // 2
        table.show()

if __name__ == '__main__':
    for path in PATHS:
        test_rendering_logic(path)
