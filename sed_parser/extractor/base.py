"""
Extractor module
"""

from __future__ import annotations
from abc import ABC, abstractmethod

import dataclasses
from datetime import datetime
import enum


class SiteList(enum.Enum):
    """SiteList"""

    DSE = "dse"


class PageTypeList(enum.Enum):
    """PageTypeList"""

    SHARE_PRICE = "sharePrice"


class FormatList(enum.Enum):
    """PageTypeList"""

    CSV = "csv"


@dataclasses.dataclass
class CommandArgs:
    """CommandArgs"""

    site: str
    page_type: str
    format: str
    data: object = ""


class Content:
    """Content"""


class PricePageContent(Content):
    """PricePageContent"""

    def __init__(self, date: str) -> None:
        self.date_on_page: datetime = datetime.strptime(date, "%b %d, %Y at %H:%M %p")


class PricePageTableContent(PricePageContent):
    """PricePageTableContent"""

    def __init__(self, header: list[str], body: list[list[str]], date: str) -> None:
        """Constructor"""

        self._header = header
        self._body = body
        super().__init__(date)

    @property
    def header(self):
        """header"""

        return self._header

    @property
    def body(self):
        """body"""

        return self._body


class Extractor(ABC):
    """Base Extractor"""

    def __init__(self, data: str) -> None:
        if not data:
            raise SystemExit("error: No data found.")

        self._data = data

    @abstractmethod
    def extract(self):
        """extract signature"""
