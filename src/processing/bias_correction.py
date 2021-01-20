from datetime import datetime as dt, timedelta
import subprocess
import sys

base = '/'.join(__file__.split('/')[:-2])
if base not in sys.path:
    sys.path.append(base)
if not base:
    base = './'

import pandas as pd
import pygrib

import config.general_settings as gs
import config.variable_settings as vs
from common.helpers import free_range, get_stations


def get_observations(stations, date_tm):
    df = pd.read_csv(f'{gs.DIR}resources/climate_obs_{date_tm.year}.csv')
    df['DATE'] = df['DATE'].apply(pd.to_datetime)
    start_bias = date_tm - timedelta(days=gs.BIAS_DAYS)
    if start_bias.year != date_tm.year:
        df_two = pd.read_csv(f'{gs.DIR}resources/climate_obs_{start_bias.year}.csv')
        df = df.append(df_two)

    df = df.loc[df['DATE'] >= start_bias]
    return df


def get_messages(date_tm, hour):
    cmd = date_tm.strftime(f'{gs.WGRIB2} {gs.DIR}models/geps/%Y%m%d%H/ens_geps_{hour:03}.grib2 -s -n')
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()
    res = p[0].decode('utf-8')
    res = (res.split('\n'))[:-1]
    names = []
    messages = []
    for key, meta in vs.metvars.items():
        names.append(key)
        for i in res:
            if 'ens mean' in i and meta['mod']['geps'][1] in i:
                messages.append(int(i.split(':')[0]))
    names.extend(['lon', 'lat'])
    messages.extend([1, 2])
    return names, messages


def get_forecasts(stations, forecast_time):
    dfs = []
    for hour in gs.ALL_TIMES:
        hour_data = {}
        names, messages = get_messages(forecast_time, hour)
        for name, message in zip(names, messages):
            with pygrib.open(forecast_time.strftime(f'{gs.DIR}models/geps/%Y%m%d%H/regrid_geps_{hour:03}.grib2')) as f:
                hour_data[name] = f.message(message)['values']
        hour_data['forecast'] = [forecast_time] * hour_data['t_max'].shape[0]
        hour_data['datetime'] = [forecast_time + timedelta(hours=hour)] * hour_data['t_max'].shape[0]
        dfs.append(pd.DataFrame(hour_data))
    data = pd.concat(dfs)
    return data


def calculate_biases(key, meta, ff):
    if meta['correction'] == 'ratio':
        cap = 5
        biases = forecasts / observations
        biases[forecasts == observations] = 1
        biases[biases > cap] = cap
        biases[biases < 1 / cap] = 1 / cap
        biases[biases != biases] = 1
    elif meta['correction'] == 'difference':
        ff[f'bias_{key}'] = ff[key] - ff[f'ob_{key}']
        ff['hour'] = (ff['datetime'] - ff['forecast']).dt.hour
        biases = ff.groupby('hour').mean().reset_index(drop=False)

    return biases


def reformat_obs(stations, observations):
    new_obs = []
    for stid in stations['stn_id'].values:
        cols = {'DATE': 'datetime', f'{stid}-TX': 'ob_t_max', f'{stid}-TN': 'ob_t_min', f'{stid}-PP': 'ob_precip'}
        df = observations[list(cols.keys())].copy()
        df.rename(columns=cols, inplace=True)
        df['stn_id'] = stid
        new_obs.append(df)
    obs = pd.concat(new_obs)
    return obs


def attach_station_ids(forecasts, stations):
    forecasts['lon'] -= 360
    forecasts[['lat', 'lon']] = forecasts[['lat', 'lon']].round(3)
    forecasts.set_index(['lat', 'lon'], inplace=True, drop=True)
    stations[['lat', 'lon']] = stations[['lat', 'lon']].round(3)
    stations.set_index(['lat', 'lon'], inplace=True, drop=True)
    forecasts = forecasts.merge(stations, left_index=True, right_index=True, how='left').reset_index(drop=False)
    return forecasts.drop_duplicates(['lat', 'lon', 'stn_id', 'datetime']).reset_index(drop=True)


def main(date_tm):
    stations = get_stations()
    stations.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
    forecasts = []
    observations = get_observations(stations, date_tm)
    days_back = gs.BIAS_DAYS + max(gs.ALL_TIMES) // 24 + 1
    for forecast_time in free_range(date_tm, date_tm - timedelta(days=days_back), timedelta(days=-1)):
        forecasts.append(get_forecasts(stations, forecast_time))
        break
    forecasts = pd.concat(forecasts)
    forecasts['day'] = forecasts.datetime.dt.day
    forecasts['month'] = forecasts.datetime.dt.month
    forecasts['year'] = forecasts.datetime.dt.year
    agg = forecasts.groupby(['lat', 'lon', 'year', 'month', 'day'])
    maxes = agg[['t_max']].max()
    mins = agg[['t_min']].min()
    acc = agg[['precip']].sum()
    forecasts = maxes.merge(mins, left_index=True, right_index=True).merge(acc, left_index=True, right_index=True).reset_index(drop=False)
    forecasts['datetime'] = forecasts.apply(lambda x: dt(int(x.year), int(x.month), int(x.day)), axis=1)

    observations = reformat_obs(stations, observations)
    # stations = stations.drop_duplicates(['lat', 'lon'])
    forecasts = attach_station_ids(forecasts, stations)
    forecasts.set_index(['stn_id', 'datetime'], inplace=True, drop=True)
    observations.set_index(['stn_id', 'datetime'], inplace=True, drop=True)
    ff = forecasts.merge(observations, how='inner', left_index=True, right_index=True)  # full_forecast
    for key, meta in vs.metvars.items():
        if meta['correction'] != 'difference':
            continue
        biases = calculate_biases(key, meta, ff)



if __name__ == '__main__':
    main(gs.ARCHIVED_RUN)
