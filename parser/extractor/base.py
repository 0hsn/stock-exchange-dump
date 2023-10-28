"""
Extractor module
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime

from parser.writer import FileWriter


site_list = ["dse"]
page_type_list = ["sharePrice"]


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


class ExtractWriter:
    """Extract Writer"""

    def __init__(self, filename_parts: list[str]) -> None:
        self.filename_parts = filename_parts

    @property
    def file_to_write(self):
        """file_to_write"""

        filename_parts = [part.lower for part in self.filename_parts]

        now = datetime.now()
        filename_parts.append(now.strftime("%Y-%m-%d"))

        return "-".join(filename_parts)

    def write(self, writer: FileWriter):
        """write to file"""

        writer.write_file(self.file_to_write)
