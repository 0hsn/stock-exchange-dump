"""
Writer module
"""

# JsonStreamWriter
# CsvStreamWriter


import abc
import sys

import typing_extensions as tx

from sed_parser.extractor.base import Content


class StreamWriter:
    """StreamWriter"""

    def __init__(self) -> None:
        """Constructor"""

        self.stream = sys.stdout
        self.content = ""

    @abc.abstractmethod
    def format(self, content: Content) -> None:
        """Print to given stream"""

    def dump(self) -> None:
        """dump"""
        print(self.content, file=self.stream)


class JsonStreamWriter(StreamWriter):
    """JsonStreamWriter"""

    @tx.override
    def format(self, content: Content) -> None:
        return super().format(content)


class CsvStreamWriter(StreamWriter):
    """CsvStreamWriter"""

    @tx.override
    def format(self, content: Content) -> None:
        return super().format(content)
