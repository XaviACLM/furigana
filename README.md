My fork of the automatic furigana superscripter. Minor differences:

is_kanji and is_hiragana return False instead of error if you pass more than one character
print_html now depends on another function, furigana_html, which returns a string - and moreover takes an optional parameter specifying the size of the furigana in rem

More importantly split_okurigana was entirely rewritten to fix some bugs. I think this is the only fork that uses regex? I haven't checked them all, but is probably more robust than the naïve approach. Importantly, it matches runs of consecutive kanji to their furigana, as opposed to guessing which kanji in the run corresponds to which kana. It's definitely possible to make it so that it **correctly** matches each kanji to its furigana, but this would require using the morphological analyzer (mecab or whichever you like) repeatedly within split_okurigana, which I cannot be bothered to do.

This is part of a project to add furigana to the anki deck for the dictionary of japanese grammar.

I leave the original readme below

# furigana
Generate furigana(振り仮名) from Japanese

It uses [MeCab](http://taku910.github.io/mecab/) (a Natural Language Toolkit) to split Japanese into words, and superscript it with furigana (振り仮名).

## Example:
### input
```
from furigana.furigana import print_html
print_html('澱んだ街角で僕らは出会った')
```
### output
<ruby><rb>澱</rb><rt>よど</rt></ruby>
ん
だ
<ruby><rb>街角</rb><rt>まちかど</rt></ruby>
で
<ruby><rb>僕</rb><rt>ぼく</rt></ruby>
ら
は
<ruby><rb>出</rb><rt>で</rt></ruby>
<ruby><rb>会</rb><rt>あ</rt></ruby>
っ
た

### input
```
from furigana.furigana import print_html
print_html('お茶にお煎餅、よく合いますね')
```

### output
お
<ruby><rb>茶</rb><rt>ちゃ</rt></ruby>
に
お
<ruby><rb>煎餅</rb><rt>せんべい</rt></ruby>
、
よく
<ruby><rb>合</rb><rt>あ</rt></ruby>
い
ます
ね

## Usage
```
$ python3 furigana.py '活版印刷の流れを汲む出版作業では'
```

# Dependency
See https://pypi.python.org/pypi/mecab-python3/0.7 <br/>
run below commands on ubuntu 
```
sudo apt-get install libmecab-dev mecab mecab-ipadic-utf8
sudo -H pip3 install mecab-python3
sudo -H pip3 install jaconv
```

# Conflict with Anaconda Python
Please use Ubuntu's original python3, not to use with Anaconda Python3
