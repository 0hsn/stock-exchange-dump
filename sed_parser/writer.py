"""
Writer module
"""

# JsonStreamWriter
# CsvStreamWriter


import abc
import csv
import io
import sys

import typing_extensions as tx

from sed_parser.extractor.base import Content, FormatList


class StreamWriter:
    """StreamWriter"""

    def __init__(self, **kwargs) -> None:
        """Constructor"""

        self.stream = (
            open(kwargs["file"], mode="w", encoding="utf-8")
            if "file" in kwargs
            else sys.stdout
        )
        self.content = ""

    def __del__(self) -> None:
        """Destructor"""

        if isinstance(self.stream, io.TextIOWrapper):
            self.stream.close()

    @abc.abstractmethod
    def format(self, content: Content) -> None:
        """Print to given stream"""


class CsvStreamWriter(StreamWriter):
    """CsvStreamWriter"""

    @tx.override
    def format(self, content: Content) -> None:
        csv_writer = csv.writer(self.stream)

        csv_writer.writerow(content.header)
        csv_writer.writerows(content.body)


def select_stream_writer(s_type: str, **kwargs) -> StreamWriter:
    """select_stream_writer"""

    if s_type == FormatList.CSV.value:
        return CsvStreamWriter(**kwargs)

    raise SystemExit("error: unsupported writer.")
