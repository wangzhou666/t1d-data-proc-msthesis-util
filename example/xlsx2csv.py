import sys

sys.path.append("/Users/zhouwang/Desktop/thesis-code")

from rulefit_data_utils import xlsx2csv_converter as xc

converter = xc.Xlsx2CsvConverter(xlsxdir="data/xlsx", csvdir="data/csv")
converter.convert()