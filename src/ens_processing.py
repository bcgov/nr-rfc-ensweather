import argparse
import sys
import shutil
from datetime import datetime as dt, timedelta
from glob import glob

import platform
if platform.system() == 'Windows':
    splitter = '\\'
else:
    splitter = '/'

base = splitter.join(__file__.split(splitter)[:-1])
if base not in sys.path:
    sys.path.append(base)
if not base:
    base = './'

from config.general_settings import VERSION, BIAS_DAYS, DIR, ALL_TIMES, FILE_SPLITTER
from config.model_settings import models
from downloads import download_models
from processing import regrid_model_data, bias_correction
from common.helpers import free_range


def get_now():
    """Trivial function created so that it can be mocked in testing

    Returns:
        dt: Current UTC time
    """
    return dt.utcnow()


def find_run_time(args):
    if args.run is not None:
        return dt.strptime(args.run, '%Y%m%d_%H')
    else:
        now = get_now()
        if now.hour < 4:
            now = (now - timedelta(days=1)).replace(hour=12)
        elif now.hour <= 16:
            now = now.replace(hour=0)
        else:
            now = now.replace(hour=12)

        return dt(now.year, now.month, now.day, now.hour)


def download_needed_runs(run_time):
    for model in models:
        for tm in free_range(run_time, run_time - timedelta(days=BIAS_DAYS), timedelta(hours=-12)):
            if tm < run_time - timedelta(days=models[model]['archived_days']):
                break
            download_models.main(model, tm)
            regrid_model_data.main(tm, model)


def delete_old_folders():
    now = get_now()
    folders = glob(f'{DIR}models/*/*')
    for folder in folders:
        base_name = folder.split(FILE_SPLITTER)[-1]
        tm = dt.strptime(base_name, '%Y%m%d%H')
        if now - timedelta(days=BIAS_DAYS+2, hours=max(ALL_TIMES)) > tm:
            shutil.rmtree(folder)


def main(args):
    if args.process and args.download:
        print('Process and Download cannot both be set to true.')
        return
    delete_old_folders()
    run_time = find_run_time(args)

    if not args.process:
        print('Downloading and Regridding data and missing runs.')
        download_needed_runs(run_time)
    if not args.download:
        print(f'Bias correcting {run_time}')
        bias_correction.main(run_time)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Main program for ensemble model processing.')
    parser.add_argument('-v', '--version', action='version', version=f'{VERSION} WeatherLogics 2021')
    parser.add_argument('-r', '--run', type=str, help='Specify run to forecast.', default=None)
    parser.add_argument('-d', '--download', help='Only download, do not process.', default=False, action='store_true')
    parser.add_argument('-p', '--process', help='Only process, do not download.', default=False, action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    main(args)
