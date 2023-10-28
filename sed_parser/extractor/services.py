"""
Extractor service
"""

from icecream import ic

from sed_parser.extractor.base import CommandArgs, SiteList, PageTypeList
from sed_parser.extractor.dse import SharePriceExtractor


class ExtractionOp:
    """Extract Writer"""

    @staticmethod
    def from_arg(args: CommandArgs) -> None:
        """parse dse share price"""

        extractor = None

        if (
            args.site == SiteList.DSE.value
            and args.page_type == PageTypeList.SHARE_PRICE.value
        ):
            extractor = SharePriceExtractor(args.data)

        if extractor:
            content = extractor.extract()
            ic(content)

        raise SystemExit("error: site or page-type mismatch.")
