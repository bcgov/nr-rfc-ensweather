import datetime as dt
import os
import sys

import numpy as np
import pandas as pd

import platform
if platform.system() == 'Windows':
    splitter = '\\'
else:
    splitter = '/'

base = splitter.join(__file__.split(splitter)[:-2])
if base not in sys.path:
    sys.path.append(base)

from config import general_settings as gs, model_settings as ms, variable_settings as vs


def free_range(start, stop, step):
    """Range iterator allowing more types than just integers

    Arguments:
        start {None} -- Start of the range
        stop {None} -- End of the range
        step {None} -- Step each time through the loop

    Raises:
        ValueError: Error thrown if start + step == start

    Yields:
        None -- Value lazily found by the iterator
    """
    if start + step == start:
        raise ValueError('Step must not be 0')
    if start < stop:
        if start + step < start:
            yield start
            return
        while start < stop:
            yield start
            start += step
    else:
        if start + step > start:
            yield start
            return
        while start > stop:
            yield start
            start += step


def get_stations():
    stations = pd.read_csv(f'{gs.DIR}resources/stations.csv')
    return stations


def fmt_orig_fn(rt, tm, m, lev=None, var=None):
    """URL formatting function (fills spots found in model settings url function)

    Args:
        rt (dt): Runtime datetime
        tm (int): Hour of forecast
        m (str): model name
        lev (int, optional): Barometric level of variable. Defaults to None.
        var (str, optional): Variable name (if gribs are separated by variables). Defaults to None.

    Returns:
        [type]: [description]
    """
    kwargs = {
        'forecast_hour_three': f'{tm:03}',
        'grib_name': var[0] if var is not None else '',
    }
    if m == 'geps':
        return (rt.strftime(ms.models['geps']['url'].format(**kwargs)), rt.strftime(ms.models['geps']['fn'].format(**kwargs)))
