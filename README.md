# dictcc-cli

Quickly look up translations without relying on the browser. This script is 
mostly just a fancy table formatter which happens to get it's data for 
formatting from dict.cc.

Features:
1. simple
2. small footprint
   - depends only on: `requests`, `beautifulsoup4` and `fake-headers`
   - `site-packages` in freshly installed VENV including all transient dependencies like `html5lib`,
     `idna`, `urllib3` is sub 20 MB!
3. scales with respect to terminal width

<br>

![dictcc-mini screenshot](https://raw.githubusercontent.com/thstkn/dictcc-mini/main/assets/screenshot.jpeg)

---
<br>

# About
I wanted a tool for the ***most convenient*** and quick access to vocab through 
cli. There is [another similar tool](https://github.com/rbaron/dict.cc.py)
already available which is more feature rich, but it has a larger dependency
footprint. I've deliberately opted against depending on rich for formatting and
lxml for parsing.

---
<br>

# How to setup

## pypi

classical: `pip install dictcc-mini`

<br>

## manual

1. Download the source code from github.
2. Install dependencies (requests, beautifulsoup4, fake_headers) with `pip install
    -r requirements.txt`.
3. I recommend aliasing in an rc-file of your shell in one of the following two
   ways. For this to work you'll need to add the `dictcc-mini/src` directory to
   you `PYTHONPATH` environment variable.

    1. ``` bash
       export PYTHONPATH=$PYTHONPATH:/your/path/to/dictcc-mini/src
       ```

    2. ``` bash
       alias dict="python3 -m dictcc_mini.cli "
       function dict() { "python3 -m dictcc_mini.cli" "$@" }
       ```

<br>

## defaults

As per my own preference, this script defaults to DE/EN as languages, which are
simply set as `DEFAULT_LANG1` and `DEFAULT_LANG2` constants in the `config.py` 
and easily modified to match your preference.

Different styles for marking multiline entries available to set in `config.py`.

---
<br>

# How to use

``` bash
# regular lookup
dict word

# to start with language selector before search use -l (--language) toggle
dict word -l

# set -f (--full) toggle full table if default 20 line table is too short 
dict word -f
```
