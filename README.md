# dictcc-cli
Quickly look up translations without relying on the browser. This script is 
mostly just a fancy table formatter which happens to get it's data for 
formatting from dict.cc.

Features:
1. very simple
2. scales with respect to terminal width

<img src="https://github.com/thstkn/dictcc-cli/blob/main/screenshot.jpeg" width="600">

---
<br>

# Why
I wanted a tool for the ***most convenient*** and quick access to vocab through my
beloved cli.

---
<br>

# How to setup
1. Edit the shebang at the top of the file to use the python interpreter of your
   choice.
2. Install dependencies (fake_headers, requests, beautifulsoup4) with `pip install
    -r requirements.txt`.
3. I recommend aliasing `search_dict_cc.py` in an rc-file of your shell in one of
   the following two ways, where -w (--word) denotes the argument for the word,
   that is to be looked up.

   ``` bash
   alias dict="$path_to/search_dict_cc.py -w "
   function dict() { "$path_to/search_dict_cc.py" -w "$@" }
   ```

4. As per my own preference, this script defaults to DE/EN as languages, which are
   simply set as `DEFAULT_LANG1` and `DEFAULT_LANG2` constants in the script. 
   Modify them as needed!

---
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
