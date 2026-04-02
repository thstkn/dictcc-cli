import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
from dictcc_mini.config import DEFAULT_LANG1, DEFAULT_LANG2

def get_url(word, fromto=None) -> str:
    if not fromto:
        fromto = f'{DEFAULT_LANG1}{DEFAULT_LANG2}'
    return f'https://{fromto}.dict.cc/?s={word}'

def scrape_for_content(url: str):
    if not url:
        print('Please supply valid URL:  {url = }')
    header = Headers().generate()
    try:
        response = requests.get(url, headers=header, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f'Error connecting to dict.cc: {e}')

def sift_the_soup(content) -> tuple[list[str], list[str]]:
    soup = BeautifulSoup(content, 'html.parser')
    table_elements = soup.find_all('td', class_='td7nl')
    table_left, table_right = [], []
    for i in range(0, len(table_elements), 2):
        l = table_elements[i]
        r = table_elements[i+1]
        table_left.append(' '.join(ref.text for ref in l.find_all(['a'])))
        table_right.append(' '.join(ref.text for ref in r.find_all(['a'])))
# dfns are optional chunks of information in brackets on dict.cc which differ
# from those brackets which are contained in the strings from a-refs above and
# need to be added extra like below
        dfns_l, dfns_r = l.find_all(['dfn']), r.find_all(['dfn'])
        if dfns_l:
            table_left[-1] += ' ' + ' '.join(f'[{d.text}]' for d in dfns_l)
        if dfns_r:
            table_right[-1] += ' ' + ' '.join(f'[{d.text}]' for d in dfns_r)
    return table_left, table_right

def scrape(word, languages) -> tuple[list[str], list[str]]:
    content = scrape_for_content(get_url(word, languages))
    return sift_the_soup(content)
