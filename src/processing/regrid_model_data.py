import os
import subprocess
import sys
from glob import glob
from time import time
from datetime import datetime as dt, timedelta

base = '/'.join(__file__.split('/')[:-2])
if base not in sys.path:
    sys.path.append(base)
if not base:
    base = './'

from common.helpers import get_stations
from config import general_settings as gs
from config import model_settings as ms


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


def ensemble_regrid(date_tm, model):
    """Regrid ensemble model from lat/lon grid to ensemble processed station locations

    Args:
        date_tm (dt): Time of forecast
        model (str): Model name
    """
    stations = get_stations()
    station_locations = convert_location_to_wgrib2(stations)

    folder = date_tm.strftime(f'{gs.DIR}models/{model}/%Y%m%d%H/')
    for hour in ms.models[model]['times']:
        regrid_file = date_tm.strftime(f'{gs.DIR}models/{model}/%Y%m%d%H/ens_{model}_{hour:03}.grib2')
        if os.path.isfile(regrid_file):
            continue

        # concatenate all hourly variable files into one grid
        cmd = f'cat {folder}*_P{hour:03}_*.grib2 > {folder}cat_{model}_{hour:03}.grib2'
        subprocess.call(cmd, shell=True)

        # regrid cat file to station locations
        cmd = f'{gs.WGRIB2} {folder}cat_{model}_{hour:03}.grib2 -new_grid location {station_locations} 0 {folder}regrid_{model}_{hour:03}.grib2'
        subprocess.call(cmd, shell=True)

        # ensemble process grid to final ens_grid
        cmd = f'{gs.WGRIB2} {folder}regrid_{model}_{hour:03}.grib2 -ens_processing {folder}ens_{model}_{hour:03}.grib2 0'
        subprocess.call(cmd, shell=True)

        # delete temporary files and ensemble files that are too small
        files = glob(date_tm.strftime(f'{folder}*{hour:03}_allmbrs.grib2'))
        files += glob(f'{folder}*{hour:03}.grib2')
        ensemble_files = [i for i in files if 'ens_' in i]
        files = [i for i in files if 'ens_' not in i]
        for i in files:
            os.remove(i)
        for i in ensemble_files:
            stats = os.stat(i)
            if stats.st_size < 1000:
                os.remove(i)


def main(date_tm, model):
    ensemble_regrid(date_tm, model)


if __name__ == '__main__':
    x_one = time()
    main(gs.ARCHIVED_RUN, 'geps')
    print(time() - x_one)
