from datetime import datetime as dt
# POSSIBLE USER SETTINGS
MAX_HOURS = 9999

DIR = '/Users/paulpries/Documents/bc_forecasting/'
WGRIB2 = '/opt/local/bin/wgrib2'


import platform
if platform.system() == 'Windows':
    FILE_SPLITTER = '\\'
else:
    FILE_SPLITTER = '/'

# NON USER SETTINGS
VERSION = 1.0

BIAS_DAYS = 15

TM_STGS = {
    'min': 6,
    'max': 384,
    'space': 6,
}

DM = {
    'lat0': 47,
    'lat1': 61,
    'lon0': -140,
    'lon1': -113,
}

ARCHIVED_RUN = dt(2021, 2, 22, 12)

MAX_RETRIES = 3
MAX_DOWNLOADS = 10

ALL_TIMES = list(range(TM_STGS['min'], TM_STGS['max'], TM_STGS['space']))
ALL_TIMES = [i for i in ALL_TIMES if i <= MAX_HOURS]
