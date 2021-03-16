import argparse
import contextlib
import logging.config
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

from config.general_settings import VERSION, BIAS_DAYS, DIR, ALL_TIMES, FILE_SPLITTER
import config.logging_config
from config.model_settings import models
from downloads import download_models
from processing import regrid_model_data, bias_correction
from common.helpers import free_range

logging.config.dictConfig(config.logging_config.LOGGING_CONFIG)
LOGGER = logging.getLogger(__name__)

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
        run_time = dt(now.year, now.month, now.day, now.hour)
        LOGGER.debug(f"run_time: {run_time}")
        return run_time


def download_needed_runs(run_time):
    LOGGER.debug(f"downloading needed runs: {run_time}")
    for model in models:
        LOGGER.debug(f"model: {model}")
        for tm in free_range(run_time, run_time - timedelta(days=BIAS_DAYS), timedelta(hours=-12)):
            if tm < run_time - timedelta(days=models[model]['archived_days']):
                break
            download_models.main(model, tm)
            regrid_model_data.main(tm, model)


def delete_old_folders():
    LOGGER.debug("checking folders to delete")
    now = get_now()
    folders = glob(f'{DIR}/models/*/*')
    for folder in folders:
        LOGGER.debug(f"folder: {folder}")
        base_name = folder.split(FILE_SPLITTER)[-1]
        LOGGER.debug(f"base_name: {base_name}")
        tm = dt.strptime(base_name, '%Y%m%d%H')
        if now - timedelta(days=BIAS_DAYS+2, hours=max(ALL_TIMES)) > tm:
            LOGGER.debug(f"removing the folder: {folder}")
            shutil.rmtree(folder)


def main(args):
    if args.process and args.download:
        #print('Process and Download cannot both be set to true.')
        LOGGER.error('Process and Download cannot both be set to true.')
        return

    try:
        delete_old_folders()
        run_time = find_run_time(args)
        LOGGER.debug(f"run_time: {run_time}")
        if not args.process:
            LOGGER.info("Downloading and Regridding data and missing runs.")
            #print('Downloading and Regridding data and missing runs.')
            if not args.verbose:
                with contextlib.redirect_stdout(None), contextlib.redirect_stderr(None):
                    download_needed_runs(run_time)
            else:
                download_needed_runs(run_time)
        if not args.download:
            print(f'Bias correcting {run_time}')
            if not args.verbose:
                with contextlib.redirect_stdout(None), contextlib.redirect_stderr(None):
                    bias_correction.main(run_time)
            else:
                bias_correction.main(run_time)
    except Exception as _:
        raise
        print('Failure running program.')


def parse_arguments():
    parser = argparse.ArgumentParser(description='Main program for ensemble model processing.')
    parser.add_argument('-v', '--version', action='version', version=f'{VERSION} WeatherLogics 2021')
    parser.add_argument('-V', '--verbose', help='Do not silence terminal output.', action='store_true', default=False)
    parser.add_argument('-r', '--run', type=str, help='Specify run to forecast. Format: yyyymmdd_hh', default=None)
    parser.add_argument('-d', '--download', help='Only download, do not process.', default=False, action='store_true')
    parser.add_argument('-p', '--process', help='Only process, do not download.', default=False, action='store_true')
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_arguments()
    main(args)
