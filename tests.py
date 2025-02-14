from furigana.furigana import _split_okurigana, repr_as_plaintext, _split_furigana_line

text = """私は知られ、愛されるだろうか？
信頼できる人はいるだろうか？
酔いがさめ始めた。
もう十分長い時間が経っただろうか？
私は知られ、愛されるだろうか？
もう少し近づいた、十分近づいた。
私は負け犬だ、気を緩めろ。
自由になるのは、きっと大変だろう。"""

"""
from furigana.mecab_importer import MeCab, CardboardMeCab
tagger_real = MeCab.Tagger("-Ochasen")
node_real = tagger_real.parseToNode(text).next
tagger_fake = CardboardMeCab.Tagger("-Ochasen")
node_fake = tagger_fake.parseToNode(text).next
for i in range(1000):
    print(node_real.surface, node_real.feature)
    print(node_real.surface, node_fake.feature)
    print("")
    node_real = node_real.next
    node_fake = node_fake.next
"""


def run_tests():
    input_output_pairs = [
        (("出会う", "であう"), "出会(であ)う"),
        (("明るい", "あかるい"), "明(あか)るい"),
        (("駆け抜け", "かけぬけ"), "駆(か)け抜(ぬ)け"),
        (("聞きました", "ききました"), "聞(き)きました"),
        (("取り締まり", "とりしまり"), "取(と)り締(し)まり"),
        (("お菓子", "おかし"), "お菓子(かし)"),
        (("エッフェル塔", "えっふぇるとう"), "エッフェル塔(とう)"),
        (("駆け駆け駆け駆け駆け", "かけかけかけかけかけ"),"駆(か)け駆(か)け駆(か)け駆(か)け駆(か)け"),
        (("駆け駆け駆け駆け駆", "かけかけかけかけか"),"駆(か)け駆(か)け駆(か)け駆(か)け駆(か)"),
        (("け駆け駆け駆け駆け", "けかけかけかけかけ"),"け駆(か)け駆(か)け駆(か)け駆(か)け"),
        (("け駆け駆け駆け駆", "けかけかけかけか"),"け駆(か)け駆(か)け駆(か)け駆(か)"),
        # not a word. this is ambiguous! result depends on implementation details
        # (('菓お菓','おおおお'),[]),
    ]


    passed_tests = True

    print("\ntesting split_okurigana\n")
    for input_, expected_output in input_output_pairs:
        actual_output = repr_as_plaintext(_split_okurigana(*input_))
        passed = actual_output == expected_output
        passed_tests *= passed
        print(f"PASSED {input_} -> {actual_output}" if passed
              else f"FAILED {input_} -> {actual_output} != {expected_output}",)

    print("\ntesting _split_furigana_line\n")
    for (input_,_), expected_output in input_output_pairs[:-4]:
        actual_output = repr_as_plaintext(_split_furigana_line(input_))
        passed = actual_output == expected_output
        passed_tests *= passed
        print(f"PASSED {input_} -> {actual_output}" if passed
              else f"FAILED {input_} -> {actual_output} != {expected_output}",)

    if passed_tests:
        print("\nPassed all tests :^)")
    else:
        raise Exception("Failed some tests")


run_tests()

