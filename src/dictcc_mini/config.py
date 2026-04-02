from os import getenv

CODES = sorted(['EN', 'SV', 'IS', 'RU', 'RO', 'FR', 'IT', 'SK', 'NL', 'PT',
                'LA', 'FI', 'ES', 'HU', 'NO', 'BG', 'HR', 'CS', 'DA', 'TR',
                'UK', 'PL', 'EO', 'SR', 'SQ', 'EL', 'BS', 'DE'])
DEFAULT_LANG1 = getenv('DICTCC_LANG1', 'de')
DEFAULT_LANG2 = getenv('DICTCC_LANG2', 'en')

DEFAULT_STYLE = getenv('DICTCC_STYLE', 'compact2')
FIELD_STYLES = {
    'wider':    ('',  '│  ', '╰╴ '),
    'wide1':    ('',  '│ ',  '╰╴'),
    'wide2':    ('',  '│ ',  '╰ '),
    'compact1': ('',  ' ',   '╰'),
    'compact2': ('',  ' ',   ' '),
    'compact3': (' ', '',    ''),
    'none':     ('',  '',    '')
}

