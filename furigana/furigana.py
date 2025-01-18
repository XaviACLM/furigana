# -*- coding: utf-8 -*-
import sys
import MeCab
import jaconv
import regex as re


hiragana_matcher = re.compile(r"([\p{IsHira}])", re.UNICODE)
kanji_matcher = re.compile(r"([\p{IsHan}])", re.UNICODE)
kanji_seq_matcher = re.compile(r"([\p{IsHan}]+)", re.UNICODE)


def is_hiragana(ch):
    return re.fullmatch(hiragana_matcher, ch) is not None


def is_kanji(ch):
    return re.fullmatch(kanji_matcher, ch) is not None


def split_okurigana(text, hiragana):
    # the choice of matching group syntax here is somewhat arbitrary
    # hopefully japanese vocabulary should be regular enough that this will never be ambiguous?
    matcher = re.sub(kanji_matcher, "(.*)", jaconv.kata2hira(text))

    furigana = re.fullmatch(matcher, hiragana).groups()
    kanji_split = re.split(kanji_seq_matcher, text)

    n_splits = len(kanji_split)
    n_kanji = n_splits // 2
    for i in range(n_kanji):
        kanji_split[1 + 2 * i] = (kanji_split[1 + 2 * i], furigana[i])
    for i in range(2, n_splits - 1, 2):
        kanji_split[i] = (kanji_split[i],)

    for limit_index in (0, -1):
        if kanji_split[limit_index] == "":
            kanji_split.pop(limit_index)
        else:
            kanji_split[limit_index] = (kanji_split[limit_index],)

    return kanji_split


def split_furigana(text):
    """MeCab has a problem if used inside a generator ( use yield instead of return  )
    The error message is:
    ```
    SystemError: <built-in function delete_Tagger> returned a result with an error set
    ```
    It seems like MeCab has bug in releasing resource
    """
    mecab = MeCab.Tagger("-Ochasen")
    # i dont think this is necessary?
    # seems like a remnant of wanting to have the node.next instruction at the start of the loop
    # mecab.parse('') # 空でパースする必要がある
    node = mecab.parseToNode(text)
    ret = []

    while node is not None:
        origin = node.surface  # もとの単語を代入
        if not origin:
            node = node.next
            continue
        # originが空のとき、漢字以外の時はふりがなを振る必要がないのでそのまま出力する
        if any(is_kanji(_) for _ in origin):
            # main repo returns surface if this fails - this is dubious
            kana = node.feature.split(",")[7]  # 読み仮名を代入
            hiragana = jaconv.kata2hira(kana)
            ret.extend(split_okurigana(origin, hiragana))
        else:
            ret.append((origin,))
        node = node.next
    return ret


def furigana_html(text, furigana_size=None):
    style_text = (
        f' style="font-size: {furigana_size}rem;"' if furigana_size is not None else ""
    )
    result = []
    for item in split_furigana(text):
        match item:
            case (kanji, hiragana):
                result.append(
                    f"<ruby><rb>{kanji}</rb><rt{style_text}>{hiragana}</rt></ruby>"
                )
            case (hiragana,):
                result.append(hiragana)
    return "".join(result)


def print_html(text):
    print(furigana_html(text))


def run_tests():
    input_output_pairs = [
        (("出会う", "であう"), [("出会", "であ"), ("う",)]),
        (("明るい", "あかるい"), [("明", "あか"), ("るい",)]),
        (("駆け抜け", "かけぬけ"), [("駆", "か"), ("け",), ("抜", "ぬ"), ("け",)]),
        (("聞きました", "ききました"), [("聞", "き"), ("きました",)]),
        (
            ("取り締まり", "とりしまり"),
            [("取", "と"), ("り",), ("締", "し"), ("まり",)],
        ),
        (("お菓子", "おかし"), [("お",), ("菓子", "かし")]),
        (("エッフェル塔", "えっふぇるとう"), [("エッフェル",), ("塔", "とう")]),
        # not a word. this is ambiguous! result depends on implementation details
        # (('菓お菓','おおおお'),[]),
    ]
    print("testing split_okurigana")
    for input_, expected_output in input_output_pairs:
        actual_output = list(split_okurigana(*input_))
        print(f"{input_} -> {actual_output} ( ?= {expected_output} )")
        assert actual_output == expected_output


def main():
    text = sys.argv[1]
    print_html(text)


if __name__ == "__main__":
    if "idlelib.run" in sys.modules:
        run_tests()
    else:
        main()
