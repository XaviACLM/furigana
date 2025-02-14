try:

    import MeCab

except ModuleNotFoundError:

    import os
    import subprocess
    from dataclasses import dataclass
    from typing import Any
    import re

    from .config import MECAB_EXE

    forced_utf8_env = os.environ.copy()
    forced_utf8_env["PYTHONUTF8"] = "1"

    # an extremely pared down interface to MeCab, usable only for the purposes of this module
    # done so that it can be easily replicated just with access to the MeCab CLI,
    # in case that this module is to be used in an environment where MeCab (the module) is not available
    #  (e.g. Anki, which has trouble with modules containing .pyd files)

    @dataclass
    class CardboardNode:
        surface: str
        feature: str
        next: Any  # Optional[CardboardNode]

    def process_mecab_cli_output_line(line: str) -> CardboardNode:
        surface, feature = line.split('\t')
        return CardboardNode(surface, feature, None)

    class CardboardMeCab:
        def __init__(self):
            self.arguments = [MECAB_EXE]

        @classmethod
        def Tagger(cls, *args):
            tagger = cls()

            # puzzlingly, the output we get if we add the -Ochasen tag is different from what you get when you look
            # at the node.features of what's returned by MeCab.parseToNode (the real one)
            # but this *is* in fact the same as what we get in the output if we do not add a format tag
            # i assume this is because MeCab (the module) emits features in a standard representation
            # which happens to be what you get if you don't pass any format arguments to the CLI
            # this means that our best approach here, instead of parsing the format ourselves,
            # is to just ignore the format argument, because the default format is already what we end up returning

            # tagger.arguments += args

            return tagger

        def parseToNode(self, text: str) -> CardboardNode:
            text = re.sub("[\r\n]","",text)
            p = subprocess.Popen(self.arguments,
                                 stdout=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True, encoding='utf-8',
                                 env=forced_utf8_env)
            stdout_data, _ = p.communicate(input=text)
            stdout_data_lines = stdout_data.splitlines()[:-1] # remove 'EOS\n'
            cardboard_nodes = list(map(process_mecab_cli_output_line, stdout_data_lines))
            for node_1, node_2 in zip(cardboard_nodes, cardboard_nodes[1:]):
                node_1.next = node_2
            cardboard_nodes[-1].next = CardboardNode('','BOS/EOS,*,*,*,*,*,*,*,*', None)
            first_node = CardboardNode('','BOS/EOS,*,*,*,*,*,*,*,*', cardboard_nodes[0])
            return first_node

    MeCab = CardboardMeCab
