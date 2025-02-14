from dataclasses import dataclass
from functools import wraps
from typing import List, Callable, Optional

import jaconv
import re

from .mecab_importer import MeCab
from .characters import allowed_characters_matcher, UnicodeRange as ur


kanji_matcher = re.compile(fr"([{ur.kanji}々])", re.UNICODE)
kanji_seq_matcher = re.compile(fr"([{ur.kanji}々]+)", re.UNICODE)


class MeCabProcessingError(Exception):
    """Raised when MeCab attempts to parse a word not in its dictionary."""
    pass


@dataclass
class KanjiWithFurigana:
    kanji: str
    furigana: str


TextWithFurigana = List[str | KanjiWithFurigana]


def repr_with_formatting(text_with_furigana: TextWithFurigana,
                         string_formatter: Callable[[str], str],
                         kanji_formatter: Callable[[KanjiWithFurigana], str]):
    """
    Takes in a sequence of strings and kanji with furigana
    Formats the entire sequence by applying the corresponding formatter to each element
    :param text_with_furigana: Text with furigana to represent as a string
    :param string_formatter: formatter that will be applied to strings within the text
    :param kanji_formatter: formatter that will be applied to kanji with furigana within the text
    :return: formatted text
    """
    final_text = []
    for element in text_with_furigana:
        match element:
            case KanjiWithFurigana(_, _) as kanji:
                final_text.append(kanji_formatter(kanji))
            case str(_) as plain_string:
                final_text.append(string_formatter(plain_string))
            case _:
                raise TypeError("An element from the list passed to furigana.repr_with_formatting has unknown type")
    return "".join(final_text)


def repr_as_plaintext(text_with_furigana: TextWithFurigana) ->  str:
    """
    :param text_with_furigana: Text with furigana to represent as a string
    :return: A string with the text, with the furigana in parens following the kanji
    """
    return repr_with_formatting(text_with_furigana,
                                lambda string: string,
                                lambda k: f"{k.kanji}({k.furigana})")


def repr_as_html(text_with_furigana: TextWithFurigana, furigana_size: Optional[float] = None) -> str:
    """
    :param text_with_furigana: Text with furigana to represent in HTML
    :param furigana_size: Desired furigana size in em
    :return: A string with the text formatted as HTML
    """
    style_text = f' style="font-size: {furigana_size}rem;"' if furigana_size is not None else ""
    return repr_with_formatting(text_with_furigana,
                                lambda string: string,
                                lambda k: f"<ruby><rb>{k.kanji}</rb><rt{style_text}>{k.furigana}</rt></ruby>")


def _split_okurigana(text: str, hiragana: str) -> TextWithFurigana:
    """
    given some text and its reading, matches each part of the reading to the corresponding kanji
    (just by what fits and what doesn't - no morphological processing here)
    e.g.
        ("駆け抜け", "かけぬけ") --> "駆(か) け 抜(ぬ) け"
        ("出会う", "であう")    --> "出会(であ) う"
    """
    # the choice of matching group syntax here is somewhat arbitrary
    # japanese vocabulary should be regular enough that this will never be ambiguous
    matcher = re.sub(kanji_matcher, "(.*)", jaconv.kata2hira(text))

    furigana = re.fullmatch(matcher, hiragana).groups()
    kanji_split = re.split(kanji_seq_matcher, text)

    n_splits = len(kanji_split)
    for i in range(1,n_splits,2):
        kanji_split[i] = KanjiWithFurigana(kanji_split[i], furigana[i//2])

    # possibly 0 == -1, but that's fine
    if kanji_split[0] == "": kanji_split.pop(0)
    if kanji_split[-1] == "": kanji_split.pop(-1)

    return kanji_split


def verify_no_unknown_characters(known_character_matcher: re.Pattern):
    def decorator(func):
        @wraps(func)
        def decorated_func(text: str, *args, check_valid: bool = False, **kwargs):
            if check_valid:
                if re.fullmatch(known_character_matcher, text) is None:
                    unknown_characters = re.sub(allowed_characters_matcher, "", text)
                    raise ValueError(f"Unknown characters passed to furigana.{func.__name__}:\n"
                                     f"\t{unknown_characters}\n"
                                     f"\trepr: {repr(unknown_characters)}\n"
                                     "It's likely that these will be silently deleted by MeCab during processing.\n"
                                     "If this is acceptable, disable this check by passing 'check_valid=False'")
            return func(text, *args, **kwargs)
        return decorated_func
    return decorator


@verify_no_unknown_characters(allowed_characters_matcher)
def _split_furigana_line(text: str, ignore_unknown_words=False) -> TextWithFurigana:
    """
    Uses MeCab to tokenize input text and add furigana to the kanji within
    Do not call this, call split_furigana
    :param text: text to be processed
    :param ignore_unknown_words: if True, kanji where no reading is found will be left without furigana
        if false, an error is thrown
    :return: TextWithFurigana, a list of strings and KanjiWithFurigana
    """
    mecab = MeCab.Tagger("-Ochasen")
    node = mecab.parseToNode(text)

    furiganized_text = []
    while node is not None:
        surface = node.surface
        if re.search(kanji_matcher, surface) is not None:
            try:
                kana = node.feature.split(",")[7]
            except IndexError:
                if ignore_unknown_words:
                    furiganized_text.append(surface)
                    node = node.next
                    continue
                raise MeCabProcessingError("MeCab could not find a reading for one of the words passed to"
                                f" furigana.split_furigana_line : {surface}\n\n"
                                "This can be handled a few different ways:\n"
                                "\t- Passing 'ignore_unknown_words=True' to the furigana function that is being used,"
                                " or --ignore-unknown if the module is being used from the CLI. This"
                                " will result in kanji being left without furigana"
                                " if an appropiate reading cannot be found\n"
                                "\t- More often than not these errors come from typos (or kyujitai kanji) in the text"
                                " that is being parsed, which can be remedied from the client code. For this purpose"
                                " there is a function furigana.furigana.find_troublesome_characters(text: str), which"
                                " will return a list of every word that MeCab is unable to find a reading for.\n"
                                "\t- If neither of the prior are suitable, the word can be added to"
                                " the MeCab dictionary - this is a bit finnicky.")
            hiragana = jaconv.kata2hira(kana)
            furiganized_text.extend(_split_okurigana(surface, hiragana))
        else:
            furiganized_text.append(surface)
        node = node.next
    return furiganized_text


def find_troublesome_characters(text: str) -> List[str]:
    """
    Helper function. Finds words within passed text for which MeCab is unable to find a reading
    :param text: text to search
    :return: list of words from text that MeCab could not find a reading for
    """
    mecab = MeCab.Tagger("-Ochasen")
    node = mecab.parseToNode(text)

    result = []
    while node is not None:
        surface = node.surface
        if re.search(kanji_matcher, surface) is not None:
            if len(node.feature.split(",")) < 8:
                result.append(surface)
        node = node.next
    return result


def split_furigana(text: str, ignore_unknown_words=False) -> TextWithFurigana:
    """
    Uses MeCab via _split_furigana_lines to tokenize input text and add furigana to the kanji within
    Wrapper around _split_furigana_lines that makes sure to separate special characters from the input
    (otherwise they are eaten up by MeCab)
    :param text: text to be processed
    :param ignore_unknown_words: if True, kanji where no reading is found will be left without furigana
        if false, an error is thrown
    :return: TextWithFurigana, a list of strings and KanjiWithFurigana
    """
    splits = re.split(allowed_characters_matcher, text)
    lines = re.findall(allowed_characters_matcher, text)
    result = []
    for split, line in zip(splits, lines):
        result.append(split)
        result.extend(_split_furigana_line(line,
                                           check_valid=False,
                                           ignore_unknown_words=ignore_unknown_words))
    result.append(splits[-1])
    return result


def add_furigana_plaintext(text: str, ignore_unknown_words=False) -> str:
    """
    adds furigana in parentheses to the kanji in the passed text
    e.g.
        "駆け抜け"  --> "駆(か)け抜(ぬ)け"
        "出会う"   --> "出会(であ)う"

    :param text: text to add furigana to
    :param ignore_unknown_words: if True, kanji where no reading is found will be left without furigana
        if false, an error is thrown
    :return: text with furigana in brackets
    """
    return repr_as_plaintext(split_furigana(text, ignore_unknown_words=ignore_unknown_words))


def add_furigana_html(text: str, furigana_size: Optional[float] = None, ignore_unknown_words=False) -> str:
    """
    adds furigana html ruby elements to the kanji in the passed text

    :param text: text to add furigana to
    :param furigana_size: text size of the furigana in em
    :param ignore_unknown_words:if True, kanji where no reading is found will be left without furigana
        if false, an error is thrown
    :return: html of the text with furigana
    """
    return repr_as_html(split_furigana(text, ignore_unknown_words=ignore_unknown_words),
                        furigana_size=furigana_size)
