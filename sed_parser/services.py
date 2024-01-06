"""
Extractor service
"""

from configparser import ConfigParser
import datetime
import pathlib

from sed_parser.extractor.base import (
    CommandArgs,
    CommandSettings,
    PricePageTableContent,
    SiteList,
    PageTypeList,
)
from sed_parser.extractor.dse import SharePriceExtractor
from sed_parser.transformers import DataFrameBuilder
from sed_parser.writer import select_stream_writer


def get_config_parser(cfg_path: str) -> ConfigParser:
    """get_filepath_for_content"""

    cfg_parser = ConfigParser()
    cfg_parser.read(cfg_path)

    return cfg_parser


class ExtractionOp:
    """Extract Writer"""

    @classmethod
    def from_arg(cls, args: CommandArgs, settings: CommandSettings) -> None:
        """parse dse share price"""

        if (
            args.site == SiteList.DSE.value
            and args.page_type == PageTypeList.SHARE_PRICE.value
        ):
            cls._process_share_price_extractor(args, settings)
        else:
            raise SystemExit("error: site or page-type mismatch.")

    @classmethod
    def _process_share_price_extractor(
        cls, args: CommandArgs, settings: CommandSettings
    ) -> None:
        """_process_share_price_extractor"""

        extractor = SharePriceExtractor(args.data)
        content = extractor.extract()

        # if content.date_on_page != datetime.datetime.now().date():
        #     raise ValueError(f"date {content.date_on_page} on the page is not today.")

        df = DataFrameBuilder.from_price_page_table_content(content)

        content_upd = PricePageTableContent.from_data_frame(df)
        content_upd.page_updated_date = content.page_updated_date

        _s_stream_path = settings.share_price_path_fmt.format(
            filename=content.date_on_page.strftime("%Y-%m-%d")
        )

        _s_path = pathlib.Path(_s_stream_path)

        if _s_path.exists():
            raise FileExistsError(f"file `{_s_stream_path}` exists already.")

        writer = select_stream_writer(args.format, **dict(file=_s_stream_path))
        writer.format(content_upd)
