from os import getenv

CODES = ['EN', 'SV', 'IS', 'RU', 'RO', 'FR', 'IT', 'SK', 'NL', 'PT', 'LA', 'FI',
         'ES', 'HU', 'NO', 'BG', 'HR', 'CS', 'DA', 'TR', 'UK', 'PL', 'EO', 'SR',
         'SQ', 'EL', 'BS', 'DE'];
CODES = list(sorted(CODES))
DEFAULT_LANG1 = getenv('DICTCC_LANG1', 'de')
DEFAULT_LANG2 = getenv('DICTCC_LANG2', 'en')

