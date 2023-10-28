"""
Writer module
"""

# JsonStreamWriter
# CsvStreamWriter


import abc
import csv
import sys

import typing_extensions as tx

from sed_parser.extractor.base import Content, FormatList


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


class CsvStreamWriter(StreamWriter):
    """CsvStreamWriter"""

    @tx.override
    def format(self, content: Content) -> None:
        csv_writer = csv.writer(self.stream)

        csv_writer.writerow(content.header)
        csv_writer.writerows(content.body)


def select_stream_writer(s_type: str) -> StreamWriter:
    """select_stream_writer"""

    if s_type == FormatList.CSV.value:
        return CsvStreamWriter()

    raise SystemExit("error: unsupported writer.")
