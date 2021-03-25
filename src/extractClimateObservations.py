"""

extracts the climate observation data from the xlsx spreadsheet to a csv file
so that ens weather scripts can consume it.

Looks in the folder os.environ["ENS_CLIMATE_OBS"]
determines the relationship between the xlsx source and the csv destinations
deleteds any csv's and regenerates them by exporting the ALL_DATa sheet 
from the corresponding xlsx file

"""
import csv
import glob
import logging.config
import openpyxl
import os
import pandas as pd

import config.logging_config

logging.config.dictConfig(config.logging_config.LOGGING_CONFIG)
LOGGER = logging.getLogger(__name__)

excelFileDir = os.environ["ENS_CLIMATE_OBS"]
excelFileGlobPattern = "ClimateDataOBS_*.xlsx"
csvFileNamePattern = "climate_obs_{year}.csv"
sheetName = 'ALL_DATA'


def convertCsvXlrd(excelFile, sheetName, csvFile):
    # print(f"sheetname: {sheetName}")
    wb = openpyxl.load_workbook(excelFile, read_only=True)
    sh = wb[sheetName]

    with open(csvFile, "w", newline="") as f:
        c = csv.writer(f)
        cnt = 0
        for r in sh.iter_rows():  # generator; was sh.rows
            c.writerow([cell.value for cell in r])
            #print(cnt)
            cnt += 1


def convertCsvPandas(excelFile, csvFileFullPath):
    """
    Doesn't work for some reason
    """
    data_xls = pd.read_excel(excelFile, sheet_name="ALL_DATA")
    data_xls.to_csv(csvFileFullPath, encoding="utf-8", index=False, header=True)


if __name__ == "__main__":
    globDir = os.path.join(excelFileDir, excelFileGlobPattern)
    LOGGER.debug(f"glob pattern: {excelFileGlobPattern}")
    excelClimateObservationFiles = glob.glob(globDir)
    for excelFile in excelClimateObservationFiles:
        LOGGER.info(f"input excelFile: {excelFile}")
        # extract the year from the filename
        excelFileBasename = os.path.basename(excelFile)
        year = os.path.splitext(excelFileBasename)[0].split("_")[1]
        LOGGER.debug(f"year from excel file parse: {year}")
        csvFileName = csvFileNamePattern.format(year=year)
        LOGGER.info(f"output csv file: {csvFileName}")
        csvFileFullPath = os.path.join(excelFileDir, csvFileName)
        if os.path.exists(csvFileFullPath):
            LOGGER.info(f"deleting the csv file: {csvFileFullPath}")
            os.remove(csvFileFullPath)
        LOGGER.info(f"dumping the sheet: {sheetName} from the file {excelFile} to {csvFileFullPath}")
        convertCsvXlrd(excelFile, sheetName, csvFileFullPath)
