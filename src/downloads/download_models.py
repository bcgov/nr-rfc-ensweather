import os
import pathlib
import shutil
import sys
import threading
import urllib.request as lib
from datetime import datetime as dt, timedelta
from glob import glob

base = '/'.join(__file__.split('/')[:-2])
if base not in sys.path:
    sys.path.append(base)
if not base:
    base = './'

from config import model_settings as ms, general_settings as gs, variable_settings as vs
from common import helpers as h


class myThread (threading.Thread):

    def __init__(self, url, cr: dt):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.url = url
        self.local_dir = gs.DIR  # ./ on mac or abs on linux
        self.cr = cr

    def run(self):
        if ('nomads' in self.url['pre'] and 'sref' not in self.url['pre']):
            sName = self.url["fname"][self.url["fname"].find('file=')+5:self.url["fname"].find('&lev')]
        else:
            sName = self.url['fname']
        print(f'STARTING: {sName}')
        self.lock.acquire()
        Download(self.url['model'], self.url['pre'],
                 self.url['fname'], self.cr)
        print(f'DONE: {sName}')
        self.lock.release()


class Download():

    def __init__(self, model, pre, fname, run: dt):
        if 'file=' in fname:
            self.fp = f'{gs.DIR}models/{model}/{run.strftime("%Y%m%d%H")}/{fname.replace("/", "_")[fname.find("file=")+5:fname.find("&")]}'
        else:
            self.fp = f'{gs.DIR}models/{model}/{run.strftime("%Y%m%d%H")}/{fname.replace("/", "_")}'
        if model == 'met_fr' and 'acc' in fname:
            self.fp = self.fp.replace('acc_0-', '')
        self.TIMEOUT = ms.models[model]['timeout']
        self.NUM_RETRIES = gs.MAX_RETRIES
        self.download_model(model, pre, fname)
        self.fails = []

    def download_model(self, m, pre, fname):

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
    path = pathlib.Path(cr.strftime(f'{gs.DIR}models/{m}/%Y%m%d%H/'))
    path.mkdir(parents=True, exist_ok=True)


def check_downloads(model, runtime, url_list):
    """If most of the model is not downloading correctly, quit downloads early

    Args:
        model (str): Name of model being downloaded
        runtime (dt): Datetime of forecast being produced
        url_list (list): List of urls

    Returns:
        bool: Whether or not downloads appear to be working correctly
    """
    expected = len(url_list)
    base = runtime.strftime(f'{gs.DIR}models/{model}/%Y%m%d%H/*')
    files = glob(base)
    exist = 0
    for i in files:
        if os.stat(i).st_size > 1000:
            exist += 1
    if exist < expected * (2/3):
        print('not working')
        return False
    return True


def main(m, date_tm, times=None):
    org_tm = date_tm
    MAX_DOWNLOADS = gs.MAX_DOWNLOADS
    # MAX_DOWNLOADS = 1
    url_list = []

    make_dir(m, date_tm)

    # check to see if the model is available at this run time
    if(date_tm.hour % ms.models[m]['cycle'] == 0):

        # create list of all urls to download. We download all models in dict
        if times is None:
            times = ms.models[m]['times']

        for t in times:
            if t > gs.TM_STGS['max']:
                break

            regrid_file = date_tm.strftime(f'{gs.DIR}models/{m}/%Y%m%d%H/ens_{m}_{t:03}.grib2')
            if os.path.isfile(regrid_file):
                continue

            if ms.models[m]['onegrib']:
                res = h.fmt_orig_fn(date_tm, t, m)
                url_list.append({'model': m, 'pre': res[0], 'fname': res[1]})
            else:
                for v in vs.metvars:
                    if '_std' in v:
                        continue
                    if((t > 0) or (t == 0 and vs.metvars[v]['acc'] is False)):

                        # if there is only surface data
                        res = h.fmt_orig_fn(date_tm, t, m, var=vs.metvars[v]['mod'][m])
                        if(res is not None):
                            url_list.append({'model': m, 'pre': res[0],
                                            'fname': res[1]})

        # start downloads in batches
        for idx, i in enumerate(range(0, len(url_list), MAX_DOWNLOADS)):
            increment = MAX_DOWNLOADS
            threads = []
            if(i + MAX_DOWNLOADS > len(url_list)):
                increment = len(url_list) - i
            threads = [myThread(url_list[j], date_tm)
                       for j in range(i, i + increment)]
            for i in threads:
                i.start()
            for t in threads:
                t.join()
            if idx == 0:
                working = check_downloads(m, date_tm, url_list[:MAX_DOWNLOADS])
                if not working:
                    break

        date_tm = org_tm
        print(f'{m.upper()} download complete!')

    else:
        print(f'The {m.upper()} is not available for cycle: {date_tm}')


if __name__ == '__main__':
    main('geps', gs.ARCHIVED_RUN)
