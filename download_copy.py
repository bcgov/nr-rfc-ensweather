import datetime as dt
from glob import glob
import os
import pathlib
import shutil
import subprocess
import sys
import threading
import urllib.request as lib

import dateutil.parser
import requests

base = '/'.join(__file__.split('/')[:-2])
if base not in sys.path:
    sys.path.append(base)
if not base:
    base = './'

from common import dicts as d, params
from process import helpers as h


class myThread (threading.Thread):

    def __init__(self, url, cr: dt.datetime):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.url = url
        self.local_dir = params.DIR  # ./ on mac or abs on linux
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

    def __init__(self, model, pre, fname, run: dt.datetime):
        if 'file=' in fname:
            self.fp = f'{params.DIR}models/{model}/{run.strftime("%Y%m%d%H")}/{fname.replace("/", "_")[fname.find("file=")+5:fname.find("&")]}'
        else:
            self.fp = f'{params.DIR}models/{model}/{run.strftime("%Y%m%d%H")}/{fname.replace("/", "_")}'
        if model == 'met_fr' and 'acc' in fname:
            self.fp = self.fp.replace('acc_0-', '')
        self.TIMEOUT = d.models[model]['timeout']
        self.NUM_RETRIES = d.MAX_RETRIES
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
                if self.fp.endswith('bz2'):
                    unzip_file(self.fp)

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

        if m not in d.ENSAVG:
            return None


def unzip_file(fp):
    cmd = f'bzip2 -d {fp}'
    subprocess.call(cmd, shell=True)


def make_dir(m, cr: dt.datetime):
    """
    Purpose:
        Make the data directory if it doesn't always exist.

    Keyword arguments:
        None

    Returns:
        None
    """
    path = pathlib.Path(f'{params.DIR}models/{m}/{cr.strftime("%Y%m%d%H")}/')
    path.mkdir(parents=True, exist_ok=True)


def check_downloads(model, runtime, url_list):
    expected = len(url_list)
    base = runtime.strftime(f'{params.DIR}models/{model}/%Y%m%d%H/*')
    files = glob(base)
    exist = 0
    for i in files:
        if os.stat(i).st_size > 1000:
            exist += 1
    if exist < expected * (2/3):
        print('not working')
        return False
    return True


def main(m, cr, times=None):

    org_tm = cr
    MAX_DOWNLOADS = d.MAX_DOWNLOADS
    # MAX_DOWNLOADS = 1
    url_list = []

    if m == 'sref':
        cr = cr - dt.timedelta(hours=3)

    make_dir(m, cr)

    # check to see if the model is available at this run time
    if(cr.hour % d.models[m]['cycle'] == 0):

        # create list of all urls to download. We download all models in dict
        if times is None:
            times = d.models[m]['times']

        for t in times:
            if t > d.TM_STGS['max']:
                break
            if m == 'sref':
                res = h.fmt_orig_fn(cr, t, m, var=[''])
                url_list.append({'model': m, 'pre': res[0], 'fname': res[1]})
                break
            elif d.models[m]['onegrib']:
                res = h.fmt_orig_fn(cr, t, m)
                url_list.append({'model': m, 'pre': res[0], 'fname': res[1]})
            else:
                for v in d.metvars:
                    if '_std' in v:
                        continue
                    if((t > 0) or (t == 0 and d.metvars[v]['acc'] is False)):

                        # if there is only surface data
                        if d.metvars[v]['mod'][m] is not None:
                            res = h.fmt_orig_fn(cr, t, m, var=d.metvars[v]['mod'][m])
                            if(res is not None):
                                url_list.append({'model': m, 'pre': res[0],
                                                'fname': res[1]})

                        # if there is upper air data
                        if d.metvars[v]['ua'] and d.metvars[v]['ua_mod'][m] is not None:
                            if not d.models[m]['one_ua']:
                                for l in d.metvars[v]['ua_mod'][m][2]:
                                    res = h.fmt_orig_fn(cr, t, m, lev=l, var=d.metvars[v]['ua_mod'][m])
                                    if(res is not None):
                                        url_list.append({'model': m, 'pre': res[0],
                                                        'fname': res[1]})
                            else:
                                res = h.fmt_orig_fn(cr, t, m, var=d.metvars[v]['ua_mod'][m])
                                if(res is not None):
                                    url_list.append({'model': m, 'pre': res[0],
                                                    'fname': res[1]})

        # start downloads in batches
        for idx, i in enumerate(range(0, len(url_list), MAX_DOWNLOADS)):
            increment = MAX_DOWNLOADS
            threads = []
            if(i + MAX_DOWNLOADS > len(url_list)):
                increment = len(url_list) - i
            threads = [myThread(url_list[j], cr)
                       for j in range(i, i + increment)]
            for i in threads:
                i.start()
            for t in threads:
                t.join()
            if idx == 0:
                working = check_downloads(m, cr, url_list[:MAX_DOWNLOADS])
                if not working:
                    break

        cr = org_tm
        print(f'{m.upper()} download complete!')

    else:
        print(f'The {m.upper()} is not available for cycle: {cr}')


if __name__ == '__main__':
    for model in ['geps']:
        main(model, params.archived_run)
