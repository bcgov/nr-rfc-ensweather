import datetime as dt
import os
import sys

import numpy as np

base = '/'.join(__file__.split('/')[:-2])
if base not in sys.path:
    sys.path.append(base)
if not base:
    base = './'

from common import dicts as d, params


def fmt_orig_fn(rt, tm, m, lev=None, var=None):
    t02 = f'{tm:02}'
    t03 = f'{tm:03}'

    kwargs = {
        'forecast_hour_three': t03,
        'forecast_hour_two': t02,
        'forecast_hour': tm,
        'var_upper': var[0].upper() if var is not None else '',
    }
    if 'nomads' not in d.models[m]['url'] or m == 'sref':
        if var is not None:
            if lev is not None and m not in {'met_fr'}:
                kwargs['level'] = lev
            else:
                kwargs['level'] = ''
            kwargs['var'] = var[0]
            if m == 'met_fr' and var[0] == 'TPRATE/surface':
                kwargs['forecast_hour'] = f'acc_0-{tm}'
            if m == 'icon':
                if lev is None:
                    kwargs['level_type'] = 'single-level'
                    kwargs['level'] = ''
                else:
                    kwargs['level_type'] = 'pressure-level'
                    kwargs['level'] = f'_{lev}'
            return (rt.strftime(d.models[m]['url'].format(**kwargs)),
                    rt.strftime(d.models[m]['fn'].format(**kwargs)))
        else:
            return None
    else:
        return fmt_ncep_fn(kwargs, m, rt)


def fmt_ncep_fn(kwargs, m, rt):
    var_s = ''
    levs = ''

    for v in d.metvars:

        # surface data exists
        if d.metvars[v]['mod'][m] is not None:

            # add surface data
            var_s = f'{var_s}&var_{d.metvars[v]["mod"][m][1]}=on'
            if d.metvars[v]['mod'][m][2].replace(' ', '_') not in levs:
                levs = f'{levs}&lev_{d.metvars[v]["mod"][m][2].replace(" ", "_")}=on'

            # add upper levels
            if d.metvars[v]['ua']:
                if d.metvars[v]['ua_mod'][m] is not None:
                    for l in d.metvars[v]['ua_mod'][m][2]:
                        if f'lev_{l}_mb' not in levs:
                            levs = f'{levs}&lev_{l}_mb=on'
                    if f'&var_{d.metvars[v]["ua_mod"][m][1]}=on' not in var_s:
                        var_s = f'{var_s}&var_{d.metvars[v]["ua_mod"][m][1]}=on'

        # no surface data
        else:
            # add upper data only
            if d.metvars[v]['ua']:
                if d.metvars[v]['ua_mod'][m] is not None:
                    var_s = f'{var_s}&var_{d.metvars[v]["ua_mod"][m][1]}=on'
                    for l in d.metvars[v]['ua_mod'][m][2]:
                        if f'lev_{l}_mb' not in levs:
                            levs = f'{levs}&lev_{l}_mb=on'

    bbox = f"&leftlon={d.dm['lon0']['full']}&rightlon={d.dm['lon1']['full']}&toplat={d.dm['lat1']}&bottomlat={d.dm['lat0']}"
    kwargs['var_box'] = var_s + bbox
    kwargs['level_var_box'] = levs + var_s + bbox
    return (rt.strftime(d.models[m]['url']), rt.strftime(d.models[m]['fn'].format(**kwargs)))


def fmt_regrid_fn(rt, tm, m):
    return f'{m}_regrid_{rt}_f{tm:03}.grib2'


def model_inv(rt, t, regridded=False):
    """
    Purpose:
        Here we create a model "inventory" to determine what models
        were downloaded for the current run.

    Keyword arguments:
        None

    Return:
        model_list -- dictionary with model names as keys and their values
                        True or False based on whether the model was
                        downloaded for the given run time.
    """
    if regridded:
        rg = '_regrid' # add regrid to end of model name
    else:
        rg = ''
    model_list = {}
    fdr = rt.strftime('%Y%m%d%H')

    for m in d.models:
        if m == 'sref':
            fdr = (rt - dt.timedelta(hours=3)).strftime('%Y%m%d%H')
            t = t + 3
        model_list[m] = False

        # make sure the time is possible for this model
        if(t <= max(d.models[m]['times'])):

            # get the current and previous file times
            p, c = find_times(t, m)

            # if the difference is greater than 1, need to check both
            # the current and previous files to see if time exists
            if(c-p) > 1 and c > 0:
                fn_p = fmt_regrid_fn(fdr, p, m)
                fn_c = fmt_regrid_fn(fdr, c, m)
                if(os.path.isfile(f'{params.DIR}models/{m}{rg}/{fdr}/{fn_p}') and
                   os.path.isfile(f'{params.DIR}models/{m}{rg}/{fdr}/{fn_c}')):
                    model_list[m] = True
            # if the time diff is just 1, only need to check current tm
            else:
                fn = fmt_regrid_fn(fdr, c, m)
                if(os.path.isfile(f'{params.DIR}models/{m}{rg}/{fdr}/{fn}')):
                    model_list[m] = True

        if m == 'sref':
            fdr = rt.strftime('%Y%m%d%H')
            t = t - 3

    return model_list


def find_times(tm, m, mv=None):
    """
    Purpose:
        Given the current desired forecast time, what model files should
        we open to use as the current file and the previous file.
        E.g. if the time is 4 and we have model data at hours 0, 3, 6, and
        9, we should open file 6 as current and 3 as previous.

    Keyword arguments:
        tm -- the desired forecast time as an integer
        m -- the model name

    Returns
        grbs -- the current and previous file times to use
    """
    # RDPS CAPE is not available at all normal times
    times = d.models[m]['times']
    if m == 'rdps' and mv == 'cape':
        times = list(range(0, 85, 3))
    elif m == 'gdps' and mv == 'cape' and tm > 168:
        times = list(range(168, 241, 6))

    mtm = min(filter(lambda x: x >= tm, times))
    i = times.index(mtm)
    if(i == 0):
        return -1, mtm
    else:
        return times[i-1], mtm
