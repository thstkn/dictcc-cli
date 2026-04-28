from urllib.request import Request, urlopen
from urllib.parse import quote
from html.parser import HTMLParser
from dictcc_mini.config import DEFAULT_LANG1, DEFAULT_LANG2, DEFAULT_HEADERS

def scrape_for_content(word: str, languages) -> str:
    ''' Returns decoded html string '''
    url = get_url(word, languages)
    if not url:
        raise ValueError(f'Please supply valid URL:  {url = }')
    req = Request(url, headers=DEFAULT_HEADERS)
    try:
        with urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f'scrape_for_content: Error connecting to dict.cc: {e}')

def get_columns(word: str, languages) -> tuple[list[str], list[str]]:
    content = scrape_for_content(word, languages)
    if not content:
        raise ValueError(f'Got no content from `scrape_for_content()`!')
    parser = DictParser()
    parser.feed(content)
    table_left, table_right = parser.data[0::2], parser.data[1::2]
    return table_left, table_right

def get_url(word, langs=None) -> str:
    if not langs:
        langs = f'{DEFAULT_LANG1}{DEFAULT_LANG2}'
    safe_word = quote(word)     # quote to make compatible with umlauts
    return f'https://{langs}.dict.cc/?s={safe_word}'

class DictParser(HTMLParser):
    def __init__(self, show_frequency=False):
        super().__init__()
        self.data = []
        self.show_frequency = show_frequency
        self.in_target_td = False       # state flags
        self.in_dfn = False
        self.in_ignored_div = False
        self.main_buffer = []
        self.tag_buffer = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'td' and attrs_dict.get('class') == 'td7nl':
            self.in_target_td = True
        elif self.in_target_td:
            if tag == 'dfn':
                self.in_dfn = True
            elif tag == 'div' and 'color:#999' in attrs_dict.get('style', ''):
                if not self.show_frequency:
                    self.in_ignored_div = True

    def handle_data(self, data):
        if self.in_target_td and not self.in_ignored_div:
            clean_text = data.strip()
            if clean_text:
                if self.in_dfn:
                    self.tag_buffer.append(f'[{clean_text}]')
                else:
                    self.main_buffer.append(clean_text)

    def handle_endtag(self, tag):
        if tag == 'dfn':
            self.in_dfn = False
        elif tag == 'div':
            self.in_ignored_div = False
        elif tag == 'td' and self.in_target_td:
            # reassemble text first, then tags
            entry = " ".join(self.main_buffer)
            if self.tag_buffer:
                entry += " " + " ".join(self.tag_buffer)
            if entry.strip():
                self.data.append(entry.strip())
            self.main_buffer = []   # reset buffers and state for next entry
            self.tag_buffer = []
            self.in_target_td = False
