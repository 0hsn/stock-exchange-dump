"""
Writer module
"""
import abc
import csv
import pathlib


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
