"""
Extractor service
"""
from configparser import ConfigParser

from sed_parser.extractor.base import (
    CommandArgs,
    CommandSettings,
    SiteList,
    PageTypeList,
)
from sed_parser.extractor.dse import SharePriceExtractor
from sed_parser.writer import select_stream_writer


def get_config_parser(cfg_path: str) -> ConfigParser:
    """get_filepath_for_content"""

    cfg_parser = ConfigParser()
    cfg_parser.read(cfg_path)

    return cfg_parser


class ExtractionOp:
    """Extract Writer"""

    @staticmethod
    def from_arg(args: CommandArgs, settings: CommandSettings) -> None:
        """parse dse share price"""

        extractor = None

        if (
            args.site == SiteList.DSE.value
            and args.page_type == PageTypeList.SHARE_PRICE.value
        ):
            extractor = SharePriceExtractor(args.data)

        if extractor:
            content = extractor.extract()

            _s_stream_path = settings.share_price_path_fmt.format(
                filename=content.date_on_page.strftime("%Y-%m-%d")
            )

            writer = select_stream_writer(args.format, **dict(file=_s_stream_path))
            writer.format(content)

            return

        raise SystemExit("error: site or page-type mismatch.")
