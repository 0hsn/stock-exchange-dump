"""
Writer module
"""
import abc
import csv
import pathlib


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


class FileWriter(abc.ABC):
    """Base class for file writing utilities"""

    @abc.abstractmethod
    def write_file(self, file_path: pathlib.Path, content: Content):
        """write_file interface"""


class CsvFileWriter(FileWriter):
    """CsvFileWriter"""

    def write_file(self, file_path: pathlib.Path, content: CsvContent):
        """Write to given csv file"""

        file_to_write = str(file_path.resolve())
        with open(file_to_write, encoding="utf8") as resource:
            csv_writer = csv.writer(resource)

            csv_writer.writerow(content.header)
            csv_writer.writerows(content.body)
