import datetime as dt
import logging
import os
import sys
import pathlib
import NRUtil.NRObjStoreUtil as NRObjStoreUtil

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

LOGGER = logging.getLogger(__name__)

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
    #stations_path = pathlib.Path(f'{gs.SRCDIR}/resources/stations.csv')
    stations_path = os.path.join({gs.SRCDIR},'resources/stations.csv')
    stations = pd.read_csv(str(stations_path))
    LOGGER.debug(f"stations path: {stations_path}, {len(stations)}")
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
    if m in ['geps','reps']:
        geps_url = (rt.strftime(ms.models[m]['url'].format(**kwargs)), rt.strftime(ms.models[m]['fn'].format(**kwargs)))
        LOGGER.debug(f'geps_url: {geps_url}') 
        return geps_url

def send_to_objstore(download_folder):
    ostore = NRObjStoreUtil.ObjectStoreUtil()
    files = os.listdir(download_folder)
    for i in files:
        ostore.put_object(local_path=os.path.join(download_folder,i), ostore_path=os.path.join(gs.OBJSTORE,download_folder,i))

def get_from_objstore(folder_path):
    ostore = NRObjStoreUtil.ObjectStoreUtil()
    obj_files = ostore.list_objects(os.path.join(gs.OBJSTORE,folder_path),return_file_names_only=True)
    local_fpaths = os.listdir(folder_path)
    local_fnames = [path.split('/')[-1] for path in local_fpaths]
    for i in obj_files:
        fname = i.split("/")[-1]
        if fname not in local_fnames:
            ostore.get_object(local_path=os.path.join(folder_path,fname), file_path=i)

