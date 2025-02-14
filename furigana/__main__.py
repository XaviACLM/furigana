#!/usr/bin/env python3

import argparse
import sys

from . import add_furigana_plaintext, add_furigana_html
from .furigana import find_troublesome_characters

def get_parser():
    parser = argparse.ArgumentParser(
        description="Process Japanese text and add furigana (readings) in plaintext or HTML."
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Plaintext Furigana Command
    plaintext_parser = subparsers.add_parser(
        "plaintext",
        help="Convert text to furigana-annotated plaintext (kanji followed by readings in parentheses).",
    )
    add_common_args(plaintext_parser)

    # HTML Furigana Command
    html_parser = subparsers.add_parser(
        "html",
        help="Convert text to furigana-annotated HTML with <ruby> tags.",
    )
    add_common_args(html_parser)
    html_parser.add_argument(
        "--furigana-size",
        type=float,
        default=0.8,
        help="Size of furigana text in em (default: 0.8)."
    )

    # Troublesome Characters Command
    trouble_parser = subparsers.add_parser(
        "troublesome",
        help="Find words that MeCab cannot process properly.",
    )
    add_common_args(trouble_parser)

    return parser


def add_common_args(subparser):
    """Adds common input/output arguments to a subparser."""
    subparser.add_argument(
        "input",
        nargs="?",
        type=str,
        help="Input text or path to input file (reads from stdin if omitted)."
    )
    subparser.add_argument(
        "-i", "--inputfile",
        nargs="?",
        type=str,
        help="Input text or path to input file (reads from stdin if omitted)."
    )
    subparser.add_argument(
        "-o", "--outputfile",
        type=str,
        help="Path to output file (prints to stdout if omitted)."
    )
    subparser.add_argument(
        "--ignore-unknown",
        action="store_true",
        help="Ignore unknown words (disable strict validation)."
    )


def read_input(args):
    """Reads input from a file or stdin."""
    source = args.inputfile
    if source:
        try:
            with open(source, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            sys.exit(f"Error: File not found: {source}")
    elif args.input:
        return args.input
    return sys.stdin.read()


def write_output(destination, content):
    """Writes output to a file or stdout."""
    if destination:
        with open(destination, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        print(content)


def process_command(args):
    """Processes the CLI command."""
    input_text = read_input(args)

    if args.command == "plaintext":
        output = add_furigana_plaintext(input_text, ignore_unknown_words=args.ignore_unknown)
    elif args.command == "html":
        output = add_furigana_html(input_text, furigana_size=args.furigana_size,
                                   ignore_unknown_words=args.ignore_unknown)
    elif args.command == "troublesome":
        troublesome_words = find_troublesome_characters(input_text)
        output = "\n".join(troublesome_words) if troublesome_words else "No troublesome characters found."

    write_output(args.outputfile, output)

def main():
    parser = get_parser()
    args = parser.parse_args()
    process_command(args)

if __name__ == "__main__":
    main()
