import sys

import platform
if platform.system() == 'Windows':
    splitter = '\\'
else:
    splitter = '/'

base = splitter.join(__file__.split(splitter)[:-2])
if base not in sys.path:
    sys.path.append(base)

from config.general_settings import ALL_TIMES

models = {
    'reps': {
        # model download url base path
        'url': 'https://hpfx.collab.science.gc.ca/%Y%m%d/WXO-DD/ensemble/reps/grib2/%H/{forecast_hour_three}/',
        # model download url file path
        'fn': '%Y%m%dT%HZ_MSC_REPS_{grib_name}_RLatLon0.09x0.09_PT{forecast_hour_three}H.grib2',
        # number of days of forecasts expected to be found archived by the forecast creator. (Environment Canada in this case)
        'archived_days': 3,
        # list of times available for download (and needed for download)
        'times': list(range(0, 72, 3)),
        # download timeout (in seconds)
        'timeout': 30,
        # number of ensemble members included in model statistics
        'ensemble_members': 20,
    },
    'geps': {
        # model download url base path
        #'url': 'https://dd.weather.gc.ca/ensemble/geps/grib2/raw/%H/{forecast_hour_three}/',
        'url': 'https://hpfx.collab.science.gc.ca/%Y%m%d/WXO-DD/ensemble/geps/grib2/raw/%H/{forecast_hour_three}/',
        # model download url file path
        'fn': 'CMC_geps-raw_{grib_name}_latlon0p5x0p5_%Y%m%d%H_P{forecast_hour_three}_allmbrs.grib2',
        # number of days of forecasts expected to be found archived by the forecast creator. (Environment Canada in this case)
        'archived_days': 3,
        # list of times available for download (and needed for download)
        'times': (list(range(75, 192, 3)) + list(range(198, 384, 6))),
        # download timeout (in seconds)
        'timeout': 30,
        # number of ensemble members included in model statistics
        'ensemble_members': 20,
    },
}

# truncate model time list if general settings hours have been reduced
for m in models.keys():
    models[m]['times'] = [i for i in models[m]['times'] if i in ALL_TIMES or i == 0]
