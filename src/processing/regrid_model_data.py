import subprocess
import sys
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
    locs = []
    for lat, lon in zip(stations['latitude'].values, stations['longitude'].values):
        locs.append(f'{lon}:{lat}')
    return ':'.join(locs)


def ensemble_regrid(date_tm):
    stations = get_stations()
    station_locations = convert_location_to_wgrib2(stations)
    folder = date_tm.strftime(f'{gs.DIR}models/geps/%Y%m%d%H/')
    for hour in ms.models['geps']['times']:
        cmd = f'cat {folder}*_P{hour:03}_*.grib2 > {folder}cat_geps_{hour:03}.grib2'
        subprocess.call(cmd, shell=True)
        # cmd = f'{gs.WGRIB2} {folder}cat_geps_{hour:03}.grib2 -small_grib {gs.DM["lon0"]-1}:{gs.DM["lon1"]+1} {gs.DM["lat0"]-1}:{gs.DM["lat1"]+1} {folder}small_geps_{hour:03}.grib2'
        # subprocess.call(cmd, shell=True)
        cmd = f'{gs.WGRIB2} {folder}cat_geps_{hour:03}.grib2 -new_grid location {station_locations} 0 {folder}regrid_geps_{hour:03}.grib2'
        subprocess.call(cmd, shell=True)
        cmd = f'{gs.WGRIB2} {folder}regrid_geps_{hour:03}.grib2 -ens_processing {folder}ens_geps_{hour:03}.grib2 0'
        subprocess.call(cmd, shell=True)


def main(date_tm):
    ensemble_regrid(date_tm)


if __name__ == '__main__':
    x_one = time()
    main(gs.ARCHIVED_RUN)
    print(time() - x_one)
