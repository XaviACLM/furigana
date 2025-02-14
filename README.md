My fork of the automatic furigana superscripter. Install as a package with `py -m pip install git+https://github.com/XaviACLM/furigana`, use as `import furigana`.

In most settings you will be better off using yomikata or pykakasi, the main reason this exists nowadays is to avoid having too many dependencies in environments that may have trouble linking .pyd files. Namely the only non-standard python package it depends on is jaconv (which is essentially a library of substitution tables). It *will* use the MeCab module if available, but otherwise it will simply interface with the MeCab CLI - for this you need to specify the path to mecab.exe in `config.py`.

You will probably only want to deal with the functions:

`add_furigana_plaintext(text: str, ignore_unknown_words=False) -> str`

`add_furigana_html(text: str, furigana_size: Optional[float] = None, ignore_unknown_words=False) -> str`

They do what their names imply. `ignore_unknown_words` is for words where MeCab is unable to find a reading - if this is set to True, they will simply be left without furigana, otherwise the script will throw an error. This can be useful at times since often these errors are due to typos in the material that is being parsed - to this end there is also the function

`find_troublesome_characters(text: str) -> List[str]`

which will return a list of every token in the text that MeCab cannot find a reading for.

The package comes with a CLI that exposes these same three functions through `furigana plaintext`, `furigana html` and `furigana troublesome`. Input is read from the first arg or an input file if passed with `-i`, output goes to stdout or an output file if passed with `-o`, and there are arguments for `--ignore-unknown` and `--furigana-size`.

This package is forked from [MikimotoH's](https://github.com/MikimotoH/furigana). It has a bit of a theseus' ship situation going on - it originally only existed to deal with a few bugs in `_split_okurigana`, but at this point less than 5 lines remain from the original repo.
