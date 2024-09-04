# dictcc-cli
Quickly look up translations without relying on the browser. This script is 
mostly just a fancy table formatter which happens to get it's data for 
formatting from dict.cc.

Features:
1. very simple
2. scales with respect to terminal width

<img src="https://github.com/thstkn/dictcc-cli/blob/main/screenshot.jpeg" width="600">

<br>

# Why
I wanted a tool for the _*most convenient*_ and quick access to vocab through my
beloved cli.

<br>

# How to setup
This script depends on some libs from pypi: fake_headers, requests,
beautifulsoup4. Install with `pip install -r requirements.txt`.

I recommend aliasing `search_dict_cc.py` in an rc-file of your shell in one of
the following two ways, where -w (--word) denotes the argument for the word,
that is to be looked up.

``` bash
alias dict="$path_to/search_dict_cc.py -w "
function dict() { "$path_to/search_dict_cc.py" -w "$@" }
```

<br>

# How to use

``` shell
# regular lookup
dict word

# to select lanuages beforehand use -l (--language) with boolean `True` value
dict word -l True
# or
dict word -l 1

# use -f (--full) if default 20 line table is too short for your use
dict word -f
```

<br>

# How to make it yours
As per my own preference, this script defaults to DE/EN as languages, which are
simply set as `DEFAULT_LANG1` and `DEFAULT_LANG2` constants in the script. 
Modify them to your liking!
