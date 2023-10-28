"""
Extractor module
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import dataclasses
import enum


class SiteList(enum.Enum):
    """SiteList"""

    DSE = "dse"


class PageTypeList(enum.Enum):
    """PageTypeList"""

    SHARE_PRICE = "sharePrice"


@dataclasses.dataclass
class CommandArgs:
    """CommandArgs"""

    site: str
    page_type: str
    data: object = ""


class Content:
    """Content"""


class CsvContent(Content):
    """CsvContent"""

    def __init__(self, header: list[str], body: list[list[str]]) -> None:
        """Constructor"""

        self._header = header
        self._body = body

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
        self._data = data

    @abstractmethod
    def extract(self):
        """extract signature"""
