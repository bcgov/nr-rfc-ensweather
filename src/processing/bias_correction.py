from datetime import datetime as dt, timedelta
import os
import subprocess
import sys
import platform
if platform.system() == 'Windows':
    splitter = '\\'
else:
    splitter = '/'

base = splitter.join(__file__.split(splitter)[:-2])
if base not in sys.path:
    sys.path.append(base)

import numpy as np
import pandas as pd
import pygrib

import config.general_settings as gs
import config.variable_settings as vs
from config.model_settings import models
from common.helpers import free_range, get_stations


def get_observations(date_tm):
    """Pull observational data from stored csv files

    Args:
        date_tm (dt): Time of forecast run.

    Returns:
        pd.DataFrame: Observational data stored in pandas dataframe
    """
    df = pd.read_csv(f'{gs.DIR}resources/climate_obs_{date_tm.year}.csv')
    df['DATE'] = df['DATE'].apply(pd.to_datetime)
    start_bias = date_tm - timedelta(days=gs.BIAS_DAYS)
    if start_bias.year != date_tm.year:
        df_two = pd.read_csv(f'{gs.DIR}resources/climate_obs_{start_bias.year}.csv')
        df = df.append(df_two)
    df = df.loc[df['DATE'] >= start_bias]
    return df


def open_subprocess_pipe(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()
    return p[0].decode('utf-8')


def get_messages(path, model):
    """Find the message numbers for the grib files that we want. (ens mean, variable percentiles)

    Args:
        path (int): File path for the grib we want messages for
        model (str): Name of the meteorological model grib

    Returns:
        tuple: Correlated lists of names and grib message numbers
    """
    cmd = f'{gs.WGRIB2} {path} -s -n'
    res = open_subprocess_pipe(cmd)
    res = (res.split('\n'))[:-1]
    names = []
    messages = []
    for key, meta in vs.metvars.items():
        for i in res:
            if meta['mod'][model][1] in i:
                if 'ens mean' in i:
                    messages.append(int(i.split(':')[0]))
                    names.append(f'{key}_mean')
                if f"{meta['ensemble_percentiles'][0]}%" in i:
                    messages.append(int(i.split(':')[0]))
                    names.append(f'{key}_lower_percentile')
                if f"{meta['ensemble_percentiles'][1]}" in i:
                    messages.append(int(i.split(':')[0]))
                    names.append(f'{key}_upper_percentile')
    names.extend(['lon', 'lat'])
    messages.extend([3, 12])
    return names, messages


def access_grib(path, message):
    with pygrib.open(path) as f:
        return f.message(message)['values']


def check_file(path):
    return os.path.isfile(path)


def get_forecast(forecast_time, model, new_forecast):
    """Open and load all old forecast data to be used for bias correction

    Args:
        forecast_time (dt): Time of the forecast
        model (str): Name of the meteorological model forecast
        new_forecast(str): Time of the new forecast being created

    Returns:
        pd.DataFrame: Sequential data of all recent forecasts
    """
    dfs = []
    for hour in gs.ALL_TIMES:
        if forecast_time + timedelta(hours=hour) < new_forecast - timedelta(days=gs.BIAS_DAYS, hours=18):
            continue  # We don't want to use extra bias days farther back then we need
                      # 6 hour bias from 20 days ago isn't needed
                      # 12 day bias from 20 days ago is needed
                      # We include the extra 18 hours to ensure we have full days to aggregate
        hour_data = {}
        try:
            path = forecast_time.strftime(f'{gs.DIR}models/{model}/%Y%m%d%H/ens_{model}_{hour:03}.grib2')
            if check_file(path):
                names, messages = get_messages(path, model)
                for name, message in zip(names, messages):
                    hour_data[name] = access_grib(path, message)
        except Exception as _:
            continue
        if not hour_data:
            continue
        hour_data['forecast'] = [forecast_time] * hour_data['t_max_mean'].shape[0]
        hour_data['datetime'] = [forecast_time + timedelta(hours=hour)] * hour_data['t_max_mean'].shape[0]
        dfs.append(pd.DataFrame(hour_data))
    if not dfs:
        return
    data = pd.concat(dfs, sort=True)
    return data


def adjust_bias_to_count(biases, counts, correction, bias_key):
    df = biases.merge(counts, left_index=True, right_index=True, suffixes=['', '_count'])
    if correction == 'ratio':
        df[bias_key] = df[bias_key] * df[f'{bias_key}_count'] + (1 - df[f'{bias_key}_count'])
    elif correction == 'difference':
        df[bias_key] = df[bias_key] * df[f'{bias_key}_count']
    return df


def calculate_biases(key, meta, ff):
    """Calculate the historical forecast bias for given variables

    Args:
        key (str): Variable name
        meta (dict): Variable information
        ff (pd.DataFrame): Full forecasts with observations attached

    Returns:
        pd.DataFrame: ff (input) with biases attached
    """
    ob_key = f'ob_{key}'
    bias_key = f'bias_{key}_mean'
    mean_key = f'{key}_mean'
    ff.loc[ff[ob_key].isna(), mean_key] = np.NaN
    if meta['correction'] == 'ratio':
        cap = 5
        biases = ff[['stn_id', 'forecast_day', ob_key, mean_key]].groupby(['stn_id', 'forecast_day']).sum()
        counts = ff[['stn_id', 'forecast_day', mean_key]].groupby(['stn_id', 'forecast_day']).count()
        counts[bias_key] = counts[mean_key] / gs.BIAS_DAYS
        counts.loc[counts[mean_key] > 1, mean_key] = 1
        biases[bias_key] = biases[mean_key] / biases[ob_key]
        biases.loc[biases[mean_key] == biases[ob_key], bias_key] = 1
        biases.drop(columns=[mean_key, ob_key], inplace=True)
        counts.drop(columns=[mean_key], inplace=True)
        biases.loc[biases[bias_key] > cap, bias_key] = cap
        biases.loc[biases[bias_key] < 1 / cap, bias_key] = 1 / cap
        biases.loc[biases[bias_key] != biases[bias_key], bias_key] = 1
        biases = adjust_bias_to_count(biases, counts, 'ratio', bias_key)
    elif meta['correction'] == 'difference':
        ff[bias_key] = ff[mean_key] - ff[ob_key]
        biases = ff[['stn_id', 'forecast_day', bias_key]].groupby(['stn_id', 'forecast_day']).mean()
        counts = ff[['stn_id', 'forecast_day', bias_key]].groupby(['stn_id', 'forecast_day']).count()
        counts[bias_key] = counts[bias_key] / gs.BIAS_DAYS
        counts.loc[counts[bias_key] > 1, bias_key] = 1  # We don't want to accidentally overcorrect due to miscalculation
        biases = adjust_bias_to_count(biases, counts, 'difference', bias_key)

    return biases


def reformat_obs(stations, observations):
    """Reformat observational data to be 5, columns wide (stn id, datetime, ob_t_max, ob_t_min, ob_precip),
    Before reformatting, each station has it's own 3 columns.

    Args:
        stations (pd.DataFrame): Station location and name data
        observations (pd.DataFrame): Station variable observational data

    Returns:
        pd.DataFrame: Reformatted observations
    """
    new_obs = []
    for stid in stations['stn_id'].values:
        cols = {'DATE': 'datetime', f'{stid}-TX': 'ob_t_max', f'{stid}-TN': 'ob_t_min', f'{stid}-PP': 'ob_precip'}
        df = observations[list(cols.keys())].copy()
        df.rename(columns=cols, inplace=True)
        df['stn_id'] = stid
        new_obs.append(df)
    obs = pd.concat(new_obs, sort=True)
    return obs.reset_index(drop=True)


def attach_station_ids(forecasts, stations):
    """Using location information, merge forecasts and stations on latitude/longitude

    Args:
        forecasts (pd.DataFrame): Forecast data
        stations (pd.DataFrame): Station location data

    Returns:
        pd.DataFrame: Forecast data with station ids attached
    """
    forecasts.loc[forecasts['lon'] > 0, 'lon'] -= 360
    coordinates = forecasts[['lat', 'lon']].values
    stations[['lat', 'lon']] = stations[['lat', 'lon']].round(3)
    station_forecasts = []
    for stn_id, lat, lon in stations[['stn_id', 'lat', 'lon']].values:
        point = np.array([lat, lon])
        dist_2 = np.sum((coordinates-point)**2, axis=1)
        point_index = np.argmin(dist_2)
        nearest_row = coordinates[point_index]
        nearest_lat = nearest_row[0]
        nearest_lon = nearest_row[1]
        df = forecasts.loc[(forecasts['lat'] == nearest_lat) & (forecasts['lon'] == nearest_lon)]
        df['stn_id'] = stn_id
        station_forecasts.append(df)
    forecasts = pd.concat(station_forecasts, sort=True)
    return forecasts.drop_duplicates(['lat', 'lon', 'stn_id', 'forecast', 'datetime']).reset_index(drop=True)


def correct_data(forecast):
    """Correct the current forecast using biases calculated from historical errors

    Args:
        forecast (pd.DataFrame): Forecast data
    """
    for key, meta in vs.metvars.items():
        for suffix in ['_mean', '_lower_percentile', '_upper_percentile']:
            key_suffix = f'{key}{suffix}'
            if meta['correction'] == 'ratio':
                forecast.loc[~forecast[f'bias_{key}_mean'].isna(), key_suffix] /= forecast.loc[~forecast[f'bias_{key}_mean'].isna(), f'bias_{key}_mean']
            elif meta['correction'] == 'difference':
                forecast.loc[~forecast[f'bias_{key}_mean'].isna(), key_suffix] -= forecast.loc[~forecast[f'bias_{key}_mean'].isna(), f'bias_{key}_mean']
            forecast[key_suffix] = forecast[key_suffix].round(1)


def reformat_to_csv(forecast, date_tm):
    """Convert the forecast dataframe and write to excel files in proper RFP format.

    Args:
        forecast (pd.DataFrame): Forecast data
        date_tm (dt): Time of the current forecast
    """
    stns = set(forecast['stn_id'].values)
    cols = [f'{i}_{j}' for i in vs.metvars.keys() for j in ['mean', 'upper_percentile', 'lower_percentile']]
    cols.append('datetime')
    dfs = []
    folder = date_tm.strftime('%Y-%m-%d')
    forecast['datetime'] = forecast['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))
    os.makedirs(f'{gs.DIR}/output/daily_raw', exist_ok=True)
    os.makedirs(f'{gs.DIR}/output/forecasts', exist_ok=True)

    writer = pd.ExcelWriter(f'{gs.DIR}/output/daily_raw/{folder}.xlsx')
    for stn in sorted(list(stns)):
        df = forecast.loc[forecast['stn_id'] == stn, cols].set_index('datetime', drop=True)
        rename = {i: f'{stn.upper()}_{i}' for i in cols if i != 'datetime'}
        df.rename(columns=rename, inplace=True)
        df.to_excel(writer, sheet_name=f'{stn}')
        dfs.append(df)
    writer.save()
    final = pd.concat(dfs, axis=1, sort=True)
    cols = [i for i in final if i.endswith('mean')]
    final = final[cols]
    rename = {i: f'{i[:-5]}' for i in cols}
    final.rename(columns=rename, inplace=True)
    final.to_excel(f'{gs.DIR}/output/forecasts/{folder}.xlsx', index=True)


def collect_forecasts(date_tm, days_back, model):
    """Open all relevant previous forecasts and concatenate them into one dataframe

    Args:
        date_tm (dt): Time of the current forecast
        days_back (int): Number of forecasts being used to bias correct
        model (str): Name of the model being corrected (model forecast)

    Returns:
        pd.DataFrame: All relevant forecasts.
    """
    forecasts = []
    for forecast_time in free_range(date_tm, date_tm - timedelta(days=days_back), timedelta(days=-1)):
        forecast = get_forecast(forecast_time, model, date_tm)
        if forecast is not None:
            forecasts.append(forecast)
    prev_forecasts = pd.concat(forecasts, sort=True)
    prev_forecasts['day'] = prev_forecasts.datetime.dt.day
    prev_forecasts['month'] = prev_forecasts.datetime.dt.month
    prev_forecasts['year'] = prev_forecasts.datetime.dt.year
    return prev_forecasts


def find_aggregate_values(prev_forecasts, date_tm):
    """Forecasts are downloaded in 6 hour increments, these need to be reduced
    to daily values.

    Args:
        prev_forecasts (pd.DataFrame): All previous forecasts

    Returns:
        pd.DataFrame: Reduced forecasts
    """
    dfs = []
    prev_forecasts.reset_index(drop=True, inplace=True)
    prev_forecasts['agg_day'] = -1
    for key, meta in vs.metvars.items():
        start_hour = meta['utc_time_start']
        start_hour += date_tm.hour
        end_hour = start_hour + meta['time_range_length']
        agg_cols = [i for i in prev_forecasts if key in i] + ['lat', 'lon', 'forecast', 'agg_day', 'datetime']
        df = prev_forecasts[agg_cols].copy()
        for idx in range(max(gs.ALL_TIMES) // 24):
            df.loc[(df['datetime'] > df['forecast'] + timedelta(hours=start_hour)) &
                   (df['datetime'] <= df['forecast'] + timedelta(hours=end_hour)), 'agg_day'] = idx
            values = df.loc[df['agg_day'] == idx].shape[0]
            if values < meta['expected_values']:
                df.loc[df['agg_day'] == idx, 'agg_day'] = -1
            start_hour += 24
            end_hour += 24
        df.drop(df.loc[df['agg_day'] == -1].index, inplace=True)
        df.drop(columns=['datetime'], inplace=True)
        agg = df.groupby(['lat', 'lon', 'forecast', 'agg_day']).agg(meta['aggregate_function'])
        dfs.append(agg)

    prev_forecasts = dfs[0]
    for df in dfs[1:]:
        prev_forecasts = prev_forecasts.merge(df, left_index=True, right_index=True, how='outer')
    prev_forecasts.reset_index(drop=False, inplace=True)
    prev_forecasts['datetime'] = prev_forecasts.apply(lambda x: (x.forecast + timedelta(days=x.agg_day, hours=date_tm.hour)).replace(hour=0), axis=1)
    return prev_forecasts


def main(date_tm):
    stations = get_stations()
    stations.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
    observations = get_observations(date_tm)
    days_back = gs.BIAS_DAYS + max(gs.ALL_TIMES) // 24 + 1
    corrected_forecasts = []
    for model in models:
        # Find all relevant forecasts
        prev_forecasts = collect_forecasts(date_tm, days_back, model)

        for key, meta in vs.metvars.items():
            if meta['unit_offset'] != 0:
                cols = [i for i in prev_forecasts if key in i]
                prev_forecasts[cols] -= meta['unit_offset']

        # split previous forecasts from the one we want to bias correct
        forecast = prev_forecasts.loc[prev_forecasts['forecast'] == date_tm]
        prev_forecasts = prev_forecasts.loc[prev_forecasts['forecast'] != date_tm]

        # Find daily values (currently split into hourly)
        prev_forecasts = find_aggregate_values(prev_forecasts, date_tm)
        forecast = find_aggregate_values(forecast, date_tm)

        observations = reformat_obs(stations, observations)

        prev_forecasts = attach_station_ids(prev_forecasts, stations.copy())
        forecast = attach_station_ids(forecast, stations.copy())

        forecast['day'] = forecast.apply(lambda x: (x.datetime - x.forecast).total_seconds() / (3600 * 24), axis=1)
        forecast.set_index(['stn_id', 'day'], drop=True, inplace=True)

        # attach observations to forecast dates
        prev_forecasts.set_index(['stn_id', 'datetime'], inplace=True, drop=True)
        observations.set_index(['stn_id', 'datetime'], inplace=True, drop=True)
        ff = prev_forecasts.merge(observations, how='left', left_index=True, right_index=True).reset_index(drop=False)  # full_forecast
        ff['forecast_day'] = ff.apply(lambda x: (x.datetime - x.forecast).total_seconds() / (3600 * 24), axis=1)

        for key, meta in vs.metvars.items():
            biases = calculate_biases(key, meta, ff)
            forecast = forecast.merge(biases, left_index=True, right_index=True, how='inner')

        correct_data(forecast)
        forecast.reset_index(drop=False, inplace=True)
        forecast['model'] = model
        corrected_forecasts.append(forecast)
    forecast = pd.concat(corrected_forecasts, sort=True)
    forecast = forecast.groupby(['stn_id', 'datetime']).mean().reset_index(drop=False)
    reformat_to_csv(forecast, date_tm)


if __name__ == '__main__':
    main(gs.ARCHIVED_RUN)
