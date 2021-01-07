import sys

base = '/'.join(__file__.split('/')[:-2])
if base not in sys.path:
    sys.path.append(base)
if not base:
    base = './'

from config.general_settings import ALL_TIMES

models = {
    'geps': {
        'url': 'https://nomads.ncep.noaa.gov/cgi-bin/filter_cmcens.pl?',
        'fn': 'file=cmc_geavg.t%Hz.pgrb2a.0p50.f{forecast_hour_three}{level_var_box}&dir=%%2Fcmce.%Y%m%d%%2F%H%%2Fpgrb2ap5',
        'lontype': 'neg',
        'cycle': 12,
        'delay': 6.25,
        'times': list(range(0, 385, 3)),
        'timeout': 30,
        'onegrib': True,
        'one_ua': False,
        'variable_regrid': False,
        'subset_grib': False,
        'regrid_software': 'wgrib2',
        'ens_average': True,
    },
}

for m in models.keys():
    models[m]['times'] = [i for i in models[m]['times'] if i in ALL_TIMES or i == 0]
