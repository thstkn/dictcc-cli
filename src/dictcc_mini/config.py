from os import getenv
import random

COUNTRY_CODES = sorted(['EN', 'SV', 'IS', 'RU', 'RO', 'FR', 'IT', 'SK', 'NL',
                        'PT', 'LA', 'FI', 'ES', 'HU', 'NO', 'BG', 'HR', 'CS',
                        'DA', 'TR', 'UK', 'PL', 'EO', 'SR', 'SQ', 'EL', 'BS',
                        'DE'])
DEFAULT_LANG1 = getenv('DICTCC_LANG1', 'de')
DEFAULT_LANG2 = getenv('DICTCC_LANG2', 'en')
DEFAULT_TABLE_LEN = getenv('DICTCC_TABLE_LEN', 10)

FIELD_DEFAULT = getenv('DICTCC_FIELD_STYLE', 'compact2')
FIELD_STYLES = {
    'wider':    ('',  '│  ', '╰╴ '),
    'wide1':    ('',  '│ ',  '╰╴'),
    'wide2':    ('',  '│ ',  '╰ '),
    'compact1': ('',  ' ',   '╰'),
    'compact2': ('',  ' ',   ' '),
    'compact3': (' ', '',    ''),
    'none':     ('',  '',    '')
}

INLINE_DEFAULT = getenv('DICTCC_INLINE_STYLE', 'default')
INLINE_STYLES = {
    'default':  (' . ', '   '),
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
]

DEFAULT_HEADERS = {
    "User-Agent": random.choice(USER_AGENTS),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Referer": "https://www.dict.cc/"
}
