import os
import xlrd
import unicodecsv

class Xlsx2CsvConverter(object):
    def __init__(self, xlsxdir=None, csvdir=None):
        assert isinstance(xlscdir, str)
        assert isinstance(csvdir, str)
        self.xlscdir = xlscdir
        self.csvdir = csvdir if csvdir[-1] == '/' else csvdir+'/'

    def convert(self):
        files = filter(lambda f: '.xlsx' in f, os.listdir(xlscdir))

        for f in files:
            wb = xlrd.open_workbook(f)
            sh = wb.sheet_by_index(0)

            filename_csv = csvdir + f.split('.')[0] + '.csv'

            with open(filename_csv, 'wb') as fcsv:
                csvwriter = unicodecsv.writer(fcsv, encoding='utf-8', delimiter=',')

                for row_number in range(0, sh.nrows):
                    row = sh.row_values(row_number)
                    new_row = map(lambda element: element.replace(',', ';') if isinstance(element, str) else element, row)
                    csvwriter.writerow(new_row)
