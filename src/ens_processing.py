import argparse
import sys
from datetime import datetime as dt

base = '/'.join(__file__.split('/')[:-1])
if base not in sys.path:
    sys.path.append(base)
if not base:
    base = './'

from config.general_settings import VERSION


def main():
    pass


def parse_arguments():
    parser = argparse.ArgumentParser(description='Main program for ensemble model processing.')
    parser.add_argument('-v', '--version', action='version', version=f'{VERSION} WeatherLogics 2021')
    parser.add_argument('-r', '--run', choices=['yyyymmdd_hh'], type=str, help='Specify run to forecast.', default=None)
    parser.add_argument('-d', '--download', help='Only download, do not process.', default=False, type=bool)
    parser.add_argument('-p', '--process', help='Only process, do not download.', default=False, type=bool)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    print(args)
    main()
