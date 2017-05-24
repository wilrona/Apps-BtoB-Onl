"""
    pyexcel_io.fileformat.csvz
    ~~~~~~~~~~~~~~~~~~~

    The lower level csvz file format handler.

    :copyright: (c) 2014-2017 by Onni Software Ltd.
    :license: New BSD License, see LICENSE for more details
"""
import csv
import zipfile

from pyexcel_io._compact import StringIO, PY2
from pyexcel_io.book import BookReader, BookWriter
from pyexcel_io.constants import DEFAULT_SHEET_NAME, FILE_FORMAT_CSVZ

from ._csv import (
    CSVinMemoryReader,
    NamedContent,
    CSVSheetWriter
)


class CSVZipSheetWriter(CSVSheetWriter):
    def __init__(self, zipfile, sheetname, file_extension, **keywords):
        self.file_extension = file_extension
        keywords['single_sheet_in_book'] = False
        CSVSheetWriter.__init__(self, zipfile, sheetname, **keywords)

    def set_sheet_name(self, name):
        self.content = StringIO()
        self.writer = csv.writer(self.content, **self._keywords)

    def close(self):
        file_name = "%s.%s" % (self._native_sheet, self.file_extension)
        self.content.seek(0)
        self._native_book.writestr(file_name, self.content.read())
        self.content.close()


class CSVZipBookReader(BookReader):
    def __init__(self):
        BookReader.__init__(self)
        self._file_type = FILE_FORMAT_CSVZ
        self.zipfile = None

    def open(self, file_name, **keywords):
        BookReader.open(self, file_name, **keywords)
        self._native_book = self._load_from_file_alike_object(self._file_name)

    def open_stream(self, file_stream, **keywords):
        BookReader.open_stream(self, file_stream, **keywords)
        self._native_book = self._load_from_file_alike_object(
            self._file_stream)

    def read_sheet(self, native_sheet):
        content = self.zipfile.read(native_sheet.payload)
        if PY2:
            sheet = StringIO(content)
        else:
            sheet = StringIO(content.decode('utf-8'))

        reader = CSVinMemoryReader(
            NamedContent(
                native_sheet.name,
                sheet
            ),
            **self._keywords
        )
        return reader.to_array()

    def close(self):
        self.zipfile.close()

    def _load_from_file_alike_object(self, file_alike_object):
        try:
            self.zipfile = zipfile.ZipFile(file_alike_object, 'r')
            sheets = [NamedContent(self._get_sheet_name(name), name)
                      for name in self.zipfile.namelist()]
            return sheets
        except zipfile.BadZipfile:
            print("StringIO instance was passed by any chance?")
            raise

    def _get_sheet_name(self, filename):
        len_of_a_dot = 1
        len_of_csv_word = 3
        name_len = len(filename) - len_of_a_dot - len_of_csv_word
        return filename[:name_len]


class CSVZipBookWriter(BookWriter):
    def __init__(self):
        BookWriter.__init__(self)
        self._file_type = FILE_FORMAT_CSVZ
        self.zipfile = None

    def open(self, file_name, **keywords):
        BookWriter.open(self, file_name, **keywords)
        self.zipfile = zipfile.ZipFile(file_name, 'w',  zipfile.ZIP_DEFLATED)

    def create_sheet(self, name):
        given_name = name
        if given_name is None:
            given_name = DEFAULT_SHEET_NAME
        writer = CSVZipSheetWriter(
            self.zipfile,
            given_name,
            self._file_type[:3],
            **self._keywords
        )
        return writer

    def close(self):
        self.zipfile.close()


_registry = {
    "file_type": FILE_FORMAT_CSVZ,
    "reader": CSVZipBookReader,
    "writer": CSVZipBookWriter,
    "stream_type": "binary",
    "mime_type": "application/zip",
    "library": "built-in"
}

exports = (_registry,)
