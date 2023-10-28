"""
Main module

usage:
    python -m parser --site [dse|cse] --page-type=[sharePrice]

sample use-case: 
    curl [URL] -s | python -m parser --site dse --page-type sharePrice
"""

from __future__ import annotations
import argparse
import typing

from parser.extractor.base import site_list, page_type_list


class CommandArgs(typing.NamedTuple):
    site: str
    page_type: str

    @staticmethod
    def from_argparse_namespace(ns: argparse.Namespace) -> CommandArgs:
        """create a CommandArgs from argparse.namespace"""

        return CommandArgs(ns.site, ns.page_type)


def setup_argument_parser() -> CommandArgs:
    """setup argument parser"""

    parser = argparse.ArgumentParser(
        prog="parser", description="Parse and store stock market data."
    )

    parser.add_argument(
        "--site",
        help="The site this page is from, ex: `dse`, ..more to come",
        required=True,
    )
    parser.add_argument(
        "--page-type",
        help="The site this page is from, ex: `sharePrice`, ..more to come",
        required=True,
    )

    args: argparse.Namespace = parser.parse_args()

    if args.site not in site_list:
        raise SystemExit(f"`--site {args.site}` not found in supported list.")

    if args.page_type not in page_type_list:
        raise SystemExit(f"`--page-type {args.page_type}` not found in supported list.")

    return CommandArgs.from_argparse_namespace(args)


if __name__ == "__main__":
    # input()

    c_args = setup_argument_parser()
