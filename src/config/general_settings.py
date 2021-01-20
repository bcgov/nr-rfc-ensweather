from datetime import datetime as dt
# POSSIBLE USER SETTINGS
MAX_HOURS = 12


# NON USER SETTINGS
VERSION = 0.1

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

DIR = '/Users/paulpries/Documents/bc_forecasting/'
ARCHIVED_RUN = dt(2021, 1, 19, 0)
WGRIB2 = '/opt/local/bin/wgrib2'

MAX_RETRIES = 3
MAX_DOWNLOADS = 10

ALL_TIMES = list(range(TM_STGS['min'], TM_STGS['max'], TM_STGS['space']))
ALL_TIMES = [i for i in ALL_TIMES if i <= MAX_HOURS]
