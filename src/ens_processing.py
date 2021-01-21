import argparse
import sys
from datetime import datetime as dt

base = '/'.join(__file__.split('/')[:-1])
if base not in sys.path:
    sys.path.append(base)
if not base:
    base = './'

from config.general_settings import VERSION
from config.model_settings import models
from downloads import download_models
from processing import regrid_model_data, bias_correction



def find_run_time(args):
    if args.run is not None:
        return dt.strptime(args.run, '%Y%m%d_%H')
    else:
        now = dt.utcnow()
        if now.hour > 12:
            hour = 12
        else:
            hour = 0
        return dt(now.year, now.month, now.day, hour)


def main(args):

    if not args.process:
        for model in models:
            download_models.main(model, dt.utcnow())
        regrid_model_data.main(dt.utcnow())
    if not args.download:
        bias_correction.main(dt.utcnow())


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
