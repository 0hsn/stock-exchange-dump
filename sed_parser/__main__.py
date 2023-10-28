"""
Main module

usage:
    python -m parser --site [dse|cse] --page-type=[sharePrice]

sample use-case: 
    curl [URL] -s | python -m parser --site dse --page-type sharePrice
"""
from __future__ import annotations
import argparse
import sys

from sed_parser.extractor.base import FormatList, SiteList, PageTypeList, CommandArgs
from sed_parser.extractor.services import ExtractionOp


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
        help="Type of page from this site, ex: `sharePrice`, ..more to come",
        required=True,
    )
    parser.add_argument(
        "--format",
        help="Expected output format, ex: `csv`, ..more to come",
        required=True,
    )

    args: argparse.Namespace = parser.parse_args()

    if args.site not in [item.value for item in SiteList]:
        raise SystemExit(f"error: `--site {args.site}` not found in supported list.")

    if args.page_type not in [item.value for item in PageTypeList]:
        raise SystemExit(
            f"error: `--page-type {args.page_type}` not found in supported list."
        )

    if args.format not in [item.value for item in FormatList]:
        raise SystemExit(
            f"error: `--format {args.format}` not found in supported list."
        )

    return CommandArgs(
        site=args.site,
        page_type=args.page_type,
        format=args.format,
        data=sys.stdin.read(),
    )


if __name__ == "__main__":
    c_args = setup_argument_parser()
    ExtractionOp.from_arg(c_args)
