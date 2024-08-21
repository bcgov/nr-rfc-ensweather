import logging
import os
import pathlib
import shutil
import sys
import threading
import urllib.request as lib
from datetime import datetime as dt, timedelta
from glob import glob
import platform
if platform.system() == 'Windows':
    splitter = '\\'
else:
    splitter = '/'

base = splitter.join(__file__.split(splitter)[:-2])

if base not in sys.path:
    sys.path.append(base)

from config import model_settings as ms, general_settings as gs, variable_settings as vs
from common import helpers as h

LOGGER = logging.getLogger(__name__)

class myThread (threading.Thread):

    def __init__(self, url, cr: dt):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.url = url
        self.cr = cr
        LOGGER.debug(f"url: {url}")

    def run(self):
        sName = self.url['fname']
        print(f'STARTING: {sName}')
        self.lock.acquire()
        Download(self.url['model'], self.url['pre'],
                 self.url['fname'], self.cr)
        print(f'DONE: {sName}')
        self.lock.release()


class Download():

    def __init__(self, model, pre, fname, run: dt):
        fp_str = f'{gs.DIR}/models/{model}/{run.strftime("%Y%m%d%H")}/{fname.replace("/", "_")}'
        self.fp = pathlib.Path(fp_str)
        LOGGER.debug(f"self.fp: {self.fp}")
        self.TIMEOUT = ms.models[model]['timeout']
        self.NUM_RETRIES = gs.MAX_RETRIES
        self.download_model(pre, fname)
        self.fails = []

    def download_model(self, pre, fname):

        # create the url
        url = pre + fname
        downloaded = 0

        while downloaded < self.NUM_RETRIES:
            try:
                # open the url
                with lib.urlopen(url, timeout=self.TIMEOUT) as \
                        response, open(self.fp, 'wb') as of:
                    shutil.copyfileobj(response, of)

                # if we get to the end, set download to max retries
                print(f'DOWNLOADED: {self.fp}')
                downloaded = self.NUM_RETRIES

            except Exception as e:
                print(f'DOWNLOAD ERROR: {url, e}')

                # we want to retry if there was an error
                print(f'RETRYING {downloaded}: {self.fp}')
                downloaded = downloaded + 1

                # if we have maxed out retries, delete the file so the
                # program doesn't think it was downloaded properly
                if(downloaded == self.NUM_RETRIES):
                    os.remove(self.fp)


def make_dir(m, cr: dt):
    """
    Purpose:
        Make the data directory if it doesn't always exist.

    Keyword arguments:
        None

    Returns:
        None
    """
    path = pathlib.Path(cr.strftime(f'{gs.DIR}/models/{m}/%Y%m%d%H/'))
    LOGGER.debug(f"creating the path: {path}")
    path.mkdir(parents=True, exist_ok=True)


def check_downloads(download_folder, expected, file_size=1000):
    """If most of the model is not downloading correctly, quit downloads early

    Args:
        model (str): Name of model being downloaded
        runtime (dt): Datetime of forecast being produced
        url_list (list): List of urls

    Returns:
        bool: Whether or not downloads appear to be working correctly
    """
    files = glob(str(download_folder))
    exist = 0
    for i in files:
        if os.stat(i).st_size > file_size:
            exist += 1
    if exist < expected * (2/3):
        LOGGER.error('not working')
        print('not working')
        return False
    return True
    
def main(m, date_tm, times=None):
    LOGGER.debug("main called from download_models")
    MAX_DOWNLOADS = gs.MAX_DOWNLOADS
    # MAX_DOWNLOADS = 1
    url_list = []

    make_dir(m, date_tm)

    # create list of all urls to download. We download all models in dict
    if times is None:
        times = ms.models[m]['times']

    for t in times:
        LOGGER.debug(f"t: {t}")
        if t > gs.TM_STGS['max']:
            break
        regrid_str = date_tm.strftime(f'{gs.DIR}/models/{m}/%Y%m%d%H/ens_{m}_{t:03}.csv')  # documenting change from grib2 to csv that I accidentally placed within the merge.
        regrid_file = pathlib.Path(regrid_str)
        LOGGER.debug(f"regrid file check: {regrid_file}")
        if os.path.isfile(regrid_file):
            LOGGER.debug(f"regrid_file: {regrid_file} exists")
            continue

        for v in vs.metvars:
            if((t > 0) or (t == 0 and v != 'precip')):
                # if there is only surface data
                res = h.fmt_orig_fn(date_tm, t, m, var=vs.metvars[v]['mod'][m])
                if(res is not None):
                    url_list.append({'model': m, 'pre': res[0],
                                    'fname': res[1]})

        # start downloads in batches
        LOGGER.debug(f"url_list: {url_list}")
        LOGGER.debug("downloading starting...")
        for idx, i in enumerate(range(0, len(url_list), MAX_DOWNLOADS)):
            threads = [myThread(url, date_tm) for url in url_list[i:i+MAX_DOWNLOADS]]
            for i in threads:
                i.start()
            for t in threads:
                t.join()
            if idx == 0:
                download_folder_str = date_tm.strftime(f'{gs.DIR}/models/{m}/%Y%m%d%H/*')
                download_folder = pathlib.Path(download_folder_str)
                LOGGER.debug(f"download_folder: {download_folder}")
                if not check_downloads(download_folder, MAX_DOWNLOADS):
                    break

        print(f'{m.upper()} download complete!')

    else:
        print(f'The {m.upper()} is not available for cycle: {date_tm}')
    download_folder = date_tm.strftime(f'{gs.DIR}/models/{m}/%Y%m%d%H/')
    h.send_to_objstore(download_folder)


if __name__ == '__main__':
    current_date = dt.now()
    latest_run = current_date.replace(hour=12)
    main('reps', latest_run)
    #main('geps', gs.ARCHIVED_RUN)
