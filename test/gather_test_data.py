#!/usr/bin/python3.15

import json
import os
from time import sleep
from dictcc_mini.scraper import get_columns, scrape_for_content

def save_raw_html(file_path, word, languages='deen'):
    content = scrape_for_content(word, languages)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Saved to {file_path}')

def gather_sample_columns(file_path, word, languages='deen'):
    left, right = get_columns(word, languages)
    sample = {
        "word": word,
        "left": left,
        "right": right
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(sample, f, indent=4, ensure_ascii=False)
    print(f"Saved to {file_path}")

if __name__ == "__main__":
    test_terms = 'was', 'kanzler', 'bremsstrahlung', 'hi', 'test'
    p = '/home/lnrd/git/_thstkn/dictcc-mini/test/data/'
    os.makedirs(name=p, exist_ok=True)
    for word in test_terms:
        gather_sample_columns(f'{p}{word}.json', word)
        sleep(1)
        save_raw_html(f'{p}{word}.html', word)
        sleep(1)
