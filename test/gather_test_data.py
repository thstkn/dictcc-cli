import json
import os
from dictcc_mini.scraper import scrape

def gather_samples():
    # Diversified terms: short, very long/complex, and common
    test_terms = ["test", "kanzler", "hi"]
    # Ensure test directory exists
    os.makedirs("/home/lnrd/git/_thstkn/dictcc-mini/test/data",
                exist_ok=True)

    for word in test_terms:
        print(f"Gathering data for: {word}...")
        left, right = scrape(word, "deen")  # default to German-English

        sample = {
            "word": word,
            "left": left,
            "right": right
        }

        file_path = f"test/data/{word}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(sample, f, indent=4, ensure_ascii=False)
        print(f"Saved to {file_path}")

if __name__ == "__main__":
    gather_samples()
