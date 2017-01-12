import sys

sys.path.append('util')

import xlsx2csv_converter as xc

converter = xc.Xlsx2CsvConverter(xlsxdir="data/xlsx", csvdir="data/csv")
converter.convert()