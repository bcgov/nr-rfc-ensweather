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


def main(args):
    if args.process and args.download:
        print('Process and Download cannot both be set to true.')
        return

    run_time = find_run_time(args)
    if not args.process:
        print('Downloading and Regridding data and missing runs.')
        # download_needed_runs(run_time)
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
