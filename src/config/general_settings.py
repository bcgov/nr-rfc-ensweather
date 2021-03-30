from datetime import datetime as dt
import os
# POSSIBLE USER SETTINGS
# max hours can be set to something lower if a shorter forecast is wanted
# 9999 is default and will allow for the full run described by TM_STGS
MAX_HOURS = 9999

# DIR = /path/to/project/repository
# path to where the output data goes
DIR = os.environ['ENS_WEATHER_DATA']

# path to the climate / weather station observations files
CLIMATE_OBS_DIR = os.environ['ENS_CLIMATE_OBS']

# Pattern used to identify climate observation files
#CLIMATE_OBS_FILE = 'climate_obs_'
CLIMATE_OBS_FILE = 'ClimateDataOBS_'

# the path to where the source code exists
# could assume if this env var isn't set that the 
# path is the dir in __file__
SRCDIR = os.environ['ENS_HOME']

# WGRIB2 = /path/to/wgrib2/executable
WGRIB2 = os.environ['WGRIB2EXEC']
# Which value should ultimately be used for the final forecast
FORECAST_COLUMN = 'median'

# Which statistical columns are wanted in the daily raw file
# OPTIONS are ['lower_percentile', 'upper_percentile', 'median', 'mean', 'max', 'min']
RAW_COLUMNS = ['lower_percentile', 'upper_percentile', 'median', 'mean', 'max', 'min']

EXCEL_VARIABLE_ORDER = ['t_max', 't_min', 'precip']


import platform
if platform.system() == 'Windows':
    FILE_SPLITTER = '\\'
else:
    FILE_SPLITTER = '/'

# NON USER SETTINGS
VERSION = 1.0

BIAS_DAYS = 15

# Forecast time range (6, 12 , 18...378, 384)
TM_STGS = {
    'min': 6,
    'max': 384,
    'space': 6,
}


# Coordinate bounds. lower left corner = (lat0, lon0) upper right = (lat1, lon1)
DM = {
    'lat0': 47,
    'lat1': 61,
    'lon0': -140,
    'lon1': -113,
}

# For testing purposes, archived run can be used to run individual modules with this run
ARCHIVED_RUN = dt(2021, 3, 20, 12)


# Number of download retries if failures occur
MAX_RETRIES = 3
# Number of threads to be used for downloading
MAX_DOWNLOADS = 10

# List of all times used for the forecast. (6, 12 , 18...378, 384)
ALL_TIMES = list(range(TM_STGS['min'], TM_STGS['max'], TM_STGS['space']))
ALL_TIMES = [i for i in ALL_TIMES if i <= MAX_HOURS]
