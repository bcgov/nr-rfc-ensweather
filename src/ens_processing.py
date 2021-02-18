import argparse
import sys
from datetime import datetime as dt, timedelta
from glob import glob

base = '/'.join(__file__.split('/')[:-1])
if base not in sys.path:
    sys.path.append(base)
if not base:
    base = './'

from config.general_settings import VERSION, BIAS_DAYS
from config.model_settings import models
from downloads import download_models
from processing import regrid_model_data, bias_correction
from common.helpers import free_range


def find_run_time(args):
    if args.run is not None:
        return dt.strptime(args.run, '%Y%m%d_%H')
    else:
        now = dt.utcnow()
        hour = 0 if 4 <= now.hour <= 16 else 12
        return dt(now.year, now.month, now.day, hour)


def download_needed_runs(run_time):
    for model in models:
        for tm in free_range(run_time, run_time - timedelta(days=BIAS_DAYS), timedelta(hours=-12)):
            if tm < run_time - timedelta(days=models[model]['archived_days']):
                break
            download_models.main(model, tm)
            regrid_model_data.main(tm, model)


def main(args):
    run_time = find_run_time(args)
    if not args.process:
        download_needed_runs(run_time)
    if not args.download:
        bias_correction.main(run_time)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Main program for ensemble model processing.')
    parser.add_argument('-v', '--version', action='version', version=f'{VERSION} WeatherLogics 2021')
    parser.add_argument('-r', '--run', choices=['yyyymmdd_hh'], type=str, help='Specify run to forecast.', default=None)
    parser.add_argument('-d', '--download', help='Only download, do not process.', default=False, type=bool)
    parser.add_argument('-p', '--process', help='Only process, do not download.', default=False, type=bool)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    main(args)
