import re


class UnicodeRange:
    hiragana = r'\u3041-\u3096'
    katakana = r'\u30A0-\u30FF'
    kanji = r'\u3400-\u4DB5\u4E00-\u9FCB\uF900-\uFA6A'


# everything regex-escaped
english_punctuation = r"\.,!\?;:\(\)\[\]{}'\"“”‘’@#$%^&*-_/+=<>|\~–—"
japanese_punctuation = "　。、！？・：％「」『』（）〔〕［］《》【】…‥ー〜〃／―"
other_full_width_chars = "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ＂＇；～"
allowed_characters_matcher = re.compile(
    fr"[a-zA-Z0-9{UnicodeRange.hiragana}{UnicodeRange.katakana}{UnicodeRange.kanji}"
    + english_punctuation + japanese_punctuation + other_full_width_chars + "]+"
)
