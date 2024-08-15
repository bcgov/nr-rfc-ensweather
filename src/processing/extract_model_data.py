import logging
import os
import pathlib
import subprocess
import sys
from glob import glob
from time import time
from datetime import datetime as dt, timedelta
import platform
import NRUtil.NRObjStoreUtil as NRObjStoreUtil
if platform.system() == 'Windows':
    splitter = '\\'
else:
    splitter = '/'

base = splitter.join(__file__.split(splitter)[:-2])
if base not in sys.path:
    sys.path.append(base)

import numpy as np
import pandas as pd
import pygrib

from common.helpers import get_stations
from config import general_settings as gs
from config import model_settings as ms
from config import variable_settings as vs

LOGGER = logging.getLogger(__name__)

def open_subprocess_pipe(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()
    return p[0].decode('utf-8')


def access_grib(path, message):
    with pygrib.open(path) as f:
        return f.message(message)['values']


def convert_location_to_wgrib2(stations):
    """Convert locations to colon separated string

    Args:
        stations (pd.DataFrame): Dataframe of station location information

    Returns:
        str: locations formatted for wgrib usage
    """
    locs = []
    for lat, lon in zip(stations['latitude'].values, stations['longitude'].values):
        locs.append(f'{lon}:{lat}')
    return ':'.join(locs)


def get_messages(path, model):
    """Find the message numbers for the grib files that we want. (ens mean, variable percentiles)

    Args:
        path (int): File path for the grib we want messages for
        model (str): Name of the meteorological model grib

    Returns:
        tuple: Correlated lists of names and grib message numbers
    """
    cmd = f'{gs.WGRIB2} {path} -s -n'
    res = open_subprocess_pipe(cmd)
    res = (res.split('\n'))[:-1]
    names = []
    messages = []
    for key, meta in vs.metvars.items():
        for i in res:
            if meta['mod'][model][1] in i and 'MM-ENS' in i:
                ensemble_member = int(i.split('ENS=')[1].split(':')[0])
                messages.append(int(i.split(':')[0]))
                names.append(f'{key}_{ensemble_member}')
    for key, name in zip(['GEOLON', 'GEOLAT'], ['lon', 'lat']):
        for i in res:
            if key in i:
                names.append(name)
                messages.append(int(i.split(':')[0]))
    return names, messages


def store_raw(df, date_tm, hour):
    os.makedirs(f'{gs.DIR}/tmp', exist_ok=True)
    df.to_csv(date_tm.strftime(f'{gs.DIR}/tmp/%Y%m%d%H_{hour:03}'), index=False)


def calculate_stats(df):
    for v in vs.metvars.keys():
        cols = [i for i in df if v in i]
        for suffix, stat in vs.funcs.items():
            df[f'{v}_{suffix}'] = stat(df[cols], axis=1)
        df.drop(columns=cols, inplace=True)

def convert_to_df(date_tm, path, hour, model):
    names, messages = get_messages(path, model)
    hour_data = {}
    for name, message in zip(names, messages):
        hour_data[name] = access_grib(path, message)
    df = pd.DataFrame(hour_data)
    return df

def convert_to_csv(date_tm, path, hour, model):
    names, messages = get_messages(path, model)
    hour_data = {}
    for name, message in zip(names, messages):
        hour_data[name] = access_grib(path, message)
    df = pd.DataFrame(hour_data)
    store_raw(df, date_tm, hour)
    calculate_stats(df)
    df.to_csv(date_tm.strftime(f'{gs.DIR}/models/{model}/%Y%m%d%H/ens_{model}_{hour:03}.csv'), index=False)

def get_from_objstore(folder_path):
    ostore = NRObjStoreUtil.ObjectStoreUtil()
    obj_files = ostore.list_objects(os.path.join(gs.OBJSTORE,folder_path),return_file_names_only=True)
    local_fpaths = os.listdir(folder_path)
    local_fnames = [path.split('/')[-1] for path in local_fpaths]
    for i in obj_files:
        fname = i.split("/")[-1]
        if fname not in local_fnames:
            ostore.get_object(local_path=os.path.join(folder_path,fname), file_path=i)

def ensemble_regrid(date_tm, model, stations):
    """Regrid ensemble model from lat/lon grid to ensemble processed station locations

    Args:
        date_tm (dt): Time of forecast
        model (str): Model name
    """
    station_locations = convert_location_to_wgrib2(stations)
    stns_per_file = 100
    stnloc_split = station_locations.split(':')
    num_stn_files = int(len(stnloc_split)/(2*stns_per_file))+1
    stn_list = []
    for n in range(num_stn_files):
        stn_list.append(":".join(stnloc_split[(2*stns_per_file*n):(2*stns_per_file*(n+1))]))
    folder_str = date_tm.strftime(f'{gs.DIR}/models/{model}/%Y%m%d%H/')
    if not os.path.exists(folder_str):
        os.makedirs(folder_str)
    get_from_objstore(folder_str)
    folder = pathlib.Path(folder_str)
    for hour in ms.models[model]['times']:
        regrid_file_str = date_tm.strftime(f'{gs.DIR}/models/{model}/%Y%m%d%H/ens_{model}_{hour:03}.csv')  # documenting change from grib2 to csv that I accidentally placed within the merge.
        regrid_file = pathlib.Path(regrid_file_str)
        LOGGER.debug(f"regridfile: {regrid_file}")
        if os.path.isfile(regrid_file):
            LOGGER.debug("regrid_file is not a file")
            continue

        # concatenate all hourly variable files into one grid
        # create windows paths
        inputFile_win = os.path.join(folder, f'*_PT{hour:03}H.grib2')
        outputFile_win = os.path.join(folder, f'cat_{model}_{hour:03}.grib2')
        # cat command is from cygwin, won't work with windows path delimeters need
        # to convert in this case windows path with forward slash delimeter
        #   - better practice would have been to concatenate using pure python!!!!
        inputFile = inputFile_win.replace(os.sep, '/')
        outputFile = outputFile_win.replace(os.sep, '/')

        LOGGER.debug(f"inputFile: {inputFile}")
        LOGGER.debug(f"outputFile: {outputFile}")

        #cmd = f'cat {folder}/*_P{hour:03}_*.grib2 > {folder}/cat_{model}_{hour:03}.grib2'
        cmd = f'cat {inputFile} > {outputFile}'
        LOGGER.debug(f"cmd: {cmd}")
        print(cmd)
        subprocess.call(cmd, shell=True)

        # regrid cat file to station locations
        # also converting back to / slash delimiters due to usage of cygwin command line
        input_grib_path = os.path.join(f'{folder}', f'cat_{model}_{hour:03}.grib2').replace(os.sep, '/')
        for n in range(num_stn_files):
            regrid_path = os.path.join(f'{folder}', f'regrid_{model}_{hour:03}_{n}.grib2').replace(os.sep, '/')
            cmd = f'{gs.WGRIB2} {input_grib_path} -new_grid location {stn_list[n]} 0 {regrid_path}'
            #cmd = f'{gs.WGRIB2} {input_grib_path} -lon {stn_list[n]}'
            p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
        #convert_to_csv(date_tm, regrid_path, hour, model)
        # ensemble process grid to final ens_grid
        # cmd = f'{gs.WGRIB2} {regrid_path} -ncpu 1 -ens_processing {folder}ens_{model}_{hour:03}.grib2 0'
        # subprocess.call(cmd, shell=True)

        # delete temporary files and ensemble files that are too small
        # should use os.path to create paths not f-strings
        files = glob(date_tm.strftime(f'{folder}/*{hour:03}_allmbrs.grib2'))
        files += glob(f'{folder}/*{hour:03}.grib2')
        ensemble_files = [i for i in files if 'ens_' in i]
        files = [i for i in files if 'ens_' not in i]
        for i in files:
            LOGGER.debug(f"deleting: {i}")
            #os.remove(i)
        for i in ensemble_files:
            stats = os.stat(i)
            if stats.st_size < 1000:
                LOGGER.debug(f"deleting {i}")
                os.remove(i)


def regrid_to_csv(date_tm, model, stations):
    folder_str = date_tm.strftime(f'{gs.DIR}/models/{model}/%Y%m%d%H/')
    folder = pathlib.Path(folder_str)
    num_stn_files = 5
    txt_dir = date_tm.strftime(f'{gs.DIR}/TXT/{model}/%Y%m%d%H/')
    if not os.path.exists(txt_dir):
        os.makedirs(txt_dir)
    os.makedirs(f'{gs.DIR}/tmp', exist_ok=True)
    for n in range(num_stn_files):
        first = True
        for hour in ms.models[model]['times']:
            regrid_path = os.path.join(f'{folder}', f'regrid_{model}_{hour:03}_{n}.grib2').replace(os.sep, '/')
            if first==True:
                df = convert_to_df(date_tm, regrid_path, hour, model)
                df["Hour"] = hour
                first = False
            else:
                df_temp = convert_to_df(date_tm, regrid_path, hour, model)
                df_temp["Hour"] = hour
                df = pd.concat([df,df_temp])
        df["StnNum"] = df.index
        for member in range(20):
            for var in vs.metvars.keys():
                output = df.pivot(columns="StnNum",index="Hour",values=f"{var}_{member+1}")
                var_symbol = var[:1].upper()
                output.to_csv(date_tm.strftime(f'{gs.DIR}/TXT/{model}/%Y%m%d%H/MB0{member+1}_{var_symbol}{n+1}.csv'), index=False, header=False)
        


def main(date_tm, model):
    stations = get_stations()
    ensemble_regrid(date_tm, model, stations)
    regrid_to_csv(date_tm, model, stations)


if __name__ == '__main__':
    x_one = time()
    current_date = dt.now()
    latest_run = current_date.replace(hour=12)
    main(latest_run, 'reps')
    #main(gs.ARCHIVED_RUN, 'geps')
    print(time() - x_one)
