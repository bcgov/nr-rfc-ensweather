from datetime import datetime as dt, timedelta
import pytest
import sys
import os
import platform
if platform.system() == 'Windows':
    splitter = '\\'
else:
    splitter = '/'

base = splitter.join(__file__.split(splitter)[:-3])
if base not in sys.path:
    sys.path.append(base)

import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal

from src.processing import bias_correction as bc
import src.config.variable_settings as vs
from src.config import general_settings as gs


@pytest.mark.integration
class Test_Integration:

    def test_true(self):
        assert True


@pytest.mark.unit
class Test_Unit:

    def test_true(self):
        assert True

    def test_get_message(self, monkeypatch):
        def fake_pipe(cmd):
            return '''
            \n3:GEOLON:ens mean:nothing
            \n12:GEOLAT:ens mean:nothing
            \n0:APCP:surface:ens max:nothing
            \n1:APCP:ens mean:nothing
            \n2:APCP:10%:nothing
            \n30:APCP:25%:nothing
            \n4:APCP:75%:nothing
            \n5:TMAX:ens min:nothing
            \n6:TMAX:ens mean:nothing
            \n7:TMAX:75%:nothing
            \n8:TMAX:25%:nothing
            \n9:TMIN:ens min:nothing
            \n10:TMIN:ens mean:nothing
            \n11:TMIN:75%:nothing
            \n14:TMIN:25%:nothing
            '''

        for key, meta in vs.metvars.items():
            vs.metvars[key]['ensemble_percentiles'] = [25, 75]
        monkeypatch.setattr(bc, 'open_subprocess_pipe', fake_pipe)
        names, messages = bc.get_messages('path', 'geps')
        exp_names = ['precip_mean',
                     'precip_lower_percentile',
                     'precip_upper_percentile',
                     't_max_mean',
                     't_max_upper_percentile',
                     't_max_lower_percentile',
                     't_min_mean',
                     't_min_upper_percentile',
                     't_min_lower_percentile',
                     'lon',
                     'lat']
        exp_messages = [1, 30, 4, 6, 7, 8, 10, 11, 14, 3, 12]
        assert names == exp_names
        assert messages == exp_messages

    def test_get_forecast(self, monkeypatch):
        def access_grib(path, message):
            if message == 1:
                return np.array([1, 2, 3]).reshape(-1, )
            elif message == 2:
                return np.array([10, 20, 30]).reshape(-1, )
            elif message == 3:
                return np.array([100, 200, 300]).reshape(-1, )

        def get_messages(path, model):
            return ['precip_mean', 't_max_mean', 't_min_mean'], [1, 2, 3]

        def check_file(path):
            if path.endswith('006.grib2') or path.endswith('012.grib2'):
                return True
            return False

        monkeypatch.setattr(bc, 'access_grib', access_grib)
        monkeypatch.setattr(bc, 'get_messages', get_messages)
        monkeypatch.setattr(bc, 'check_file', check_file)

        data = bc.get_forecast(dt(2020, 1, 1, 0), 'geps', dt(2020, 1, 2, 0)).reset_index(drop=True)
        exp = pd.DataFrame({
            'precip_mean': [1, 2, 3, 1, 2, 3],
            't_max_mean': [10, 20, 30, 10, 20, 30],
            't_min_mean': [100, 200, 300, 100, 200, 300],
            'forecast': [dt(2020, 1, 1, 0)] * 6,
            'datetime': [dt(2020, 1, 1, 6)] * 3 + [dt(2020, 1, 1, 12)] * 3,
        })
        assert_frame_equal(data, exp, check_like=True)

    def test_get_forecast_old_forecast(self, monkeypatch):
        # Pulling from an old forecast file, we only want the last few hours used in correction
        def access_grib(path, message):
            if message == 1:
                return np.array([1]).reshape(-1, )
            elif message == 2:
                return np.array([2]).reshape(-1, )
            elif message == 3:
                return np.array([3]).reshape(-1, )

        def get_messages(path, model):
            return ['precip_mean', 't_max_mean', 't_min_mean'], [1, 2, 3]

        def check_file(path):
            return True

        monkeypatch.setattr(bc, 'access_grib', access_grib)
        monkeypatch.setattr(bc, 'get_messages', get_messages)
        monkeypatch.setattr(bc, 'check_file', check_file)
        monkeypatch.setattr(bc.gs, 'BIAS_DAYS', 10)
        monkeypatch.setattr(bc.gs, 'ALL_TIMES', [i for i in gs.ALL_TIMES if i <= 240])

        data = bc.get_forecast(dt(2020, 1, 1, 0), 'geps', dt(2020, 1, 20, 0)).reset_index(drop=True)

        oldest = dt(2020, 1, 9, 6)
        exp = pd.DataFrame({
            'precip_mean': [1] * 8,
            't_max_mean': [2] * 8,
            't_min_mean': [3] * 8,
            'forecast': [dt(2020, 1, 1, 0)] * 8,
            'datetime': [oldest + timedelta(hours=i*6) for i in range(8)],
        })
        assert_frame_equal(data, exp, check_like=True)

    def test_calculate_biases(self, monkeypatch):

        def adjust_bias_to_count(biases, *args):
            return biases

        monkeypatch.setattr(bc, 'adjust_bias_to_count', adjust_bias_to_count)

        df = pd.DataFrame({
            'stn_id': ['A', 'A', 'A', 'A'],
            'forecast_day': [1, 1, 2, 2],
            't_max_mean': [10, 10, 20, 25],
            'ob_t_max': [10, 10, 15, 25],
            'precip_mean': [0, 1, 1, 2],
            'ob_precip': [0, 0, 5, 3],
        })
        exp = pd.DataFrame({
            'stn_id': ['A', 'A'],
            'forecast_day': [1, 2],
            't_max_mean': [10, 22.5],
            'ob_t_max': [10, 20],
            'bias_t_max_mean': [0, 2.5],
            'precip_mean': [1, 3],
            'ob_precip': [0, 8],
            'bias_precip_mean': [5, 3/8],
        }).set_index(['stn_id', 'forecast_day'])
        for key in ['t_max', 'precip']:
            biases = bc.calculate_biases(key, vs.metvars[key], df)
            assert_frame_equal(biases[[f'bias_{key}_mean']], exp[[f'bias_{key}_mean']])

    def test_calculate_biases_missing_observational(self, monkeypatch):
        monkeypatch.setattr(bc.gs, 'BIAS_DAYS', 2)
        df = pd.DataFrame({
            'stn_id': ['A', 'A', 'A', 'A'],
            'forecast_day': [1, 1, 2, 2],
            't_max_mean': [10, 10, 20, 25],
            'ob_t_max': [10, np.NaN, 15, np.NaN],
            'precip_mean': [0, 1, 1, 2],
            'ob_precip': [0, np.NaN, 5, np.NaN],
        })
        exp = pd.DataFrame({
            'stn_id': ['A', 'A'],
            'forecast_day': [1, 2],
            't_max_mean': [10, 22.5],
            'ob_t_max': [10, 20],
            'bias_t_max_mean': [0, 2.5],
            'bias_t_max_mean_count': [0.5, 0.5],
            'precip_mean': [1, 3],
            'ob_precip': [0, 8],
            'bias_precip_mean': [1, 6/10],
            'bias_precip_mean_count': [0.5, 0.5],
        }).set_index(['stn_id', 'forecast_day'])
        for key in ['t_max', 'precip']:
            biases = bc.calculate_biases(key, vs.metvars[key], df)
            assert_frame_equal(biases[[f'bias_{key}_mean']], exp[[f'bias_{key}_mean']])

    def test_calculate_biases_with_count(self, monkeypatch):
        monkeypatch.setattr(bc.gs, 'BIAS_DAYS', 4)
        df = pd.DataFrame({
            'stn_id': ['A', 'A', 'A', 'A'],
            'forecast_day': [1, 1, 2, 2],
            't_max_mean': [10, 10, 20, 25],
            'ob_t_max': [10, 10, 15, 25],
            'precip_mean': [0, 1, 1, 2],
            'ob_precip': [0, 0, 5, 3],
        })
        exp = pd.DataFrame({
            'stn_id': ['A', 'A'],
            'forecast_day': [1, 2],
            't_max_mean': [10, 22.5],
            'ob_t_max': [10, 20],
            'bias_t_max_mean': [0, 1.25],
            'bias_t_max_mean_count': [0.5, 0.5],
            'precip_mean': [1, 3],
            'ob_precip': [0, 8],
            'bias_precip_mean': [3, 11/16],
            'bias_precip_mean_count': [0.5, 0.5],
        }).set_index(['stn_id', 'forecast_day'])
        for key in ['t_max', 'precip']:
            biases = bc.calculate_biases(key, vs.metvars[key], df)
            assert_frame_equal(biases[[f'bias_{key}_mean']], exp[[f'bias_{key}_mean']])

    def test_reformat_obs(self):
        stations = pd.DataFrame({
            'stn_id': ['A', 'B']
        })
        obs = pd.DataFrame({
            'DATE': [1,2,3],
            'A-TX': [10, 20, 30],
            'A-TN': [0, 10, 20],
            'A-PP': [1, 5, 7],
            'B-TX': [15, 10, 35],
            'B-TN': [10, 0, 15],
            'B-PP': [0, 0, 10],
        })
        exp = pd.DataFrame({
            'datetime': [1, 2, 3, 1, 2, 3],
            'ob_t_max': [10, 20, 30, 15, 10, 35],
            'ob_t_min': [0, 10, 20, 10, 0, 15],
            'ob_precip': [1, 5, 7, 0, 0, 10],
            'stn_id': ['A', 'A', 'A', 'B', 'B', 'B']
        })
        ret = bc.reformat_obs(stations, obs)
        assert_frame_equal(ret, exp, check_like=True)

    def test_attach_station_ids(self):
        forecasts = pd.DataFrame({
            'lon': [-112+360, -114+360, -115+360],
            'lat': [50, 51, 60],
            'forecast': [10, 20, 30],
            'datetime': [1, 2, 3],
            'example_var': [10, 15, 20],
        })
        stations = pd.DataFrame({
            'lon': [-114, -115, -112],
            'lat': [51, 60, 50],
            'stn_id': ['A', 'B', 'C'],
        })
        exp = pd.DataFrame({
            'lon': [-112, -114, -115],
            'lat': [50, 51, 60],
            'forecast': [10, 20, 30],
            'datetime': [1, 2, 3],
            'example_var': [10, 15, 20],
            'stn_id': ['C', 'A', 'B'],
        }).sort_values(['stn_id', 'lat', 'lon']).reset_index(drop=True)
        ret = bc.attach_station_ids(forecasts, stations).sort_values(['stn_id', 'lat', 'lon']).reset_index(drop=True)
        assert_frame_equal(ret, exp, check_like=True)

    def test_attach_station_ids_new_station(self):
        forecasts = pd.DataFrame({
            'lon': [-112, -114, -112, -114, -115],
            'lat': [50, 51, 50, 51, 60],
            'forecast': [10, 10, 20, 20, 20],
            'datetime': [1, 1, 2, 2, 2],
            'example_var': [10, 20, 30, 40, 50],
        })
        stations = pd.DataFrame({
            'lon': [-114, -115, -112],
            'lat': [51, 60, 50],
            'stn_id': ['A', 'B', 'C'],
        })
        exp = pd.DataFrame({
            'lon': [-112, -114, -112, -114, -115],
            'lat': [50, 51, 50, 51, 60],
            'forecast': [10, 10, 20, 20, 20],
            'datetime': [1, 1, 2, 2, 2],
            'example_var': [10, 20, 30, 40, 50],
            'stn_id': ['C', 'A', 'C', 'A', 'B']
        }).sort_values(['stn_id', 'lat', 'lon']).reset_index(drop=True)
        ret = bc.attach_station_ids(forecasts, stations).sort_values(['stn_id', 'lat', 'lon']).reset_index(drop=True)
        assert_frame_equal(ret, exp, check_like=True)

    def test_attach_station_ids_new_station_no_old_forecasts(self):
        # If a new station is added that does not forecast data associated with it,
        # It will borrow the forecast data from the nearest forecasted point.
        # This borrowing should not happen for the current forecast as the most recent download
        # will know about the new forecast and interpolate to that point.
        # Old forecasts will not have this data, however, the result should be an unaffected
        # current forecast, unless if there is observational data present.
        # Future runs will have at least one forecast with the current station available and
        # will behave as the test (test_attach_station_ids_new_station)
        # test write ability
        forecasts = pd.DataFrame({
            'lon': [-112, -114, -112, -114],
            'lat': [50, 51, 50, 51],
            'forecast': [10, 10, 20, 20],
            'datetime': [1, 1, 2, 2],
            'example_var': [10, 20, 30, 40],
        })
        stations = pd.DataFrame({
            'lon': [-114, -115, -112],
            'lat': [51, 60, 50],
            'stn_id': ['A', 'B', 'C'],
        })
        exp = pd.DataFrame({
            'lon': [-112, -114, -112, -114, -114, -114],
            'lat': [50, 51, 50, 51, 51, 51],
            'forecast': [10, 10, 20, 20, 10, 20],
            'datetime': [1, 1, 2, 2, 1, 2],
            'example_var': [10, 20, 30, 40, 20, 40],
            'stn_id': ['C', 'A', 'C', 'A', 'B', 'B']
        }).sort_values(['stn_id', 'lat', 'lon']).reset_index(drop=True)
        ret = bc.attach_station_ids(forecasts, stations).sort_values(['stn_id', 'lat', 'lon']).reset_index(drop=True)
        assert_frame_equal(ret, exp, check_like=True)

    def test_attach_station_ids_remove_station(self):
        forecasts = pd.DataFrame({
            'lon': [-112, -114, -112, -114, -115],
            'lat': [50, 51, 50, 51, 60],
            'forecast': [10, 10, 20, 20, 20],
            'datetime': [1, 1, 2, 2, 2],
            'example_var': [10, 20, 30, 40, 50],
        })
        stations = pd.DataFrame({
            'lon': [-114, -112],
            'lat': [51, 50],
            'stn_id': ['A', 'C'],
        })
        exp = pd.DataFrame({
            'lon': [-112, -114, -112, -114],
            'lat': [50, 51, 50, 51],
            'forecast': [10, 10, 20, 20],
            'datetime': [1, 1, 2, 2],
            'example_var': [10, 20, 30, 40],
            'stn_id': ['C', 'A', 'C', 'A']
        }).sort_values(['stn_id', 'lat', 'lon']).reset_index(drop=True)
        ret = bc.attach_station_ids(forecasts, stations).sort_values(['stn_id', 'lat', 'lon']).reset_index(drop=True)
        assert_frame_equal(ret, exp, check_like=True)

    def test_attach_station_ids_duplicates(self):
        forecasts = pd.DataFrame({
            'lon': [-112, -114, -115, -112],
            'lat': [50, 51, 60, 50],
            'forecast': [10, 10, 10, 10],
            'datetime': [1, 1, 1, 1],
            'example_var': [10, 15, 20, 25],
        })
        stations = pd.DataFrame({
            'lon': [-114, -115, -112, -112],
            'lat': [51, 60, 50, 50],
            'stn_id': ['A', 'B', 'C', 'D'],
        })
        exp = {'A', 'B', 'C', 'D'}
        ret = bc.attach_station_ids(forecasts, stations)
        ids = set(ret['stn_id'].values)
        assert exp == ids

    def test_attach_station_ids_multiples(self):
        forecasts = pd.DataFrame({
            'lon': [-112, -114, -115, -114, -115, -114],
            'lat': [50, 51, 60, 51, 60, 51],
            'forecast': [10, 20, 30, 1, 2, 3],
            'datetime': [1, 2, 3, 4, 5, 6],
            'example_var': [10, 15, 20, 1, 2, 3],
        })
        stations = pd.DataFrame({
            'lon': [-114, -115, -112],
            'lat': [51, 60, 50],
            'stn_id': ['A', 'B', 'C'],
        })
        exp = pd.DataFrame({
            'lon': [-112, -114, -115, -114, -115, -114],
            'lat': [50, 51, 60, 51, 60, 51],
            'forecast': [10, 20, 30, 1, 2, 3],
            'datetime': [1, 2, 3, 4, 5, 6],
            'example_var': [10, 15, 20, 1, 2, 3],
            'stn_id': ['C', 'A', 'B', 'A', 'B', 'A'],
        }).sort_values(['stn_id', 'lat', 'lon']).reset_index(drop=True)
        ret = bc.attach_station_ids(forecasts, stations).sort_values(['stn_id', 'lat', 'lon']).reset_index(drop=True)
        assert_frame_equal(ret, exp, check_like=True)

    def test_attach_station_ids_not_identical(self):
        forecasts = pd.DataFrame({
            'lon': [-112, -114.1, -115, -114.1, -115, -114.1],
            'lat': [50.2, 51, 60.2, 51, 60.2, 51],
            'forecast': [10, 20, 30, 1, 2, 3],
            'datetime': [1, 2, 3, 4, 5, 6],
            'example_var': [10, 15, 20, 1, 2, 3],
        })
        stations = pd.DataFrame({
            'lon': [-114, -115.2, -112.1],
            'lat': [51.1, 60.2, 49.9],
            'stn_id': ['A', 'B', 'C'],
        })
        exp = pd.DataFrame({
            'lon': [-112, -114.1, -115, -114.1, -115, -114.1],
            'lat': [50.2, 51, 60.2, 51, 60.2, 51],
            'forecast': [10, 20, 30, 1, 2, 3],
            'datetime': [1, 2, 3, 4, 5, 6],
            'example_var': [10, 15, 20, 1, 2, 3],
            'stn_id': ['C', 'A', 'B', 'A', 'B', 'A'],
        }).sort_values(['stn_id', 'lat', 'lon']).reset_index(drop=True)
        ret = bc.attach_station_ids(forecasts, stations).sort_values(['stn_id', 'lat', 'lon']).reset_index(drop=True)
        assert_frame_equal(ret, exp, check_like=True)

    def test_correct_data(self):
        forecast = pd.DataFrame({
            't_max_mean': [10, 20, 30],
            't_max_upper_percentile': [15, 22, 37],
            't_max_lower_percentile': [5, 17, 10],
            'bias_t_max_mean': [5, -2.5, -1],
            't_min_mean': [10, 20, 30],
            't_min_upper_percentile': [15, 22, 37],
            't_min_lower_percentile': [5, 17, 10],
            'bias_t_min_mean': [5, -2.5, -1],
            'precip_mean': [0, 1.5, 4],
            'precip_upper_percentile': [1, 2.5, 5.5],
            'precip_lower_percentile': [0, 0.7, 2.1],
            'bias_precip_mean': [2, 0.5, 1],
        }).astype(float)
        exp = pd.DataFrame({
            't_max_mean': [5, 22.5, 31],
            't_max_upper_percentile': [10, 24.5, 38],
            't_max_lower_percentile': [0, 19.5, 11],
            'bias_t_max_mean': [5, -2.5, -1],
            't_min_mean': [5, 22.5, 31],
            't_min_upper_percentile': [10, 24.5, 38],
            't_min_lower_percentile': [0, 19.5, 11],
            'bias_t_min_mean': [5, -2.5, -1],
            'precip_mean': [0, 3, 4],
            'precip_upper_percentile': [0.5, 5, 5.5],
            'precip_lower_percentile': [0, 1.4, 2.1],
            'bias_precip_mean': [2, 0.5, 1],
        }).astype(float)
        bc.correct_data(forecast)
        assert_frame_equal(forecast, exp, check_like=True)

    def test_find_aggregate_values_first_day_0z(self):
        date_tm = dt(2021, 1, 10, 0)
        prev_forecasts = pd.DataFrame({
            'lat': [49.9] * 12,
            'lon': [-97.2] * 12,
            'datetime': [dt(2021, 1, 8, 6), dt(2021, 1, 8, 12), dt(2021, 1, 8, 18), dt(2021, 1, 9, 0), dt(2021, 1, 9, 6), dt(2021, 1, 9, 12),
                         dt(2021, 1, 9, 6), dt(2021, 1, 9, 12), dt(2021, 1, 9, 18), dt(2021, 1, 10, 0), dt(2021, 1, 10, 6), dt(2021, 1, 10, 12)],
            'forecast': [dt(2021, 1, 8, 0)] * 6 + [dt(2021, 1, 9, 0)] * 6,
            't_max_mean': [500, 500, 19, 22, 500, 500,  # only the third and fourth value of each row should be examined (due to time ranges used to find max temperature)
                           500, 500, 21, 18, 500, 500],
            't_min_mean': [-100, -100, -100, -100, 11, 14,    # only the last values of each row should be examined (time range of minimum temperature)
                           -100, -100, -100, -100, 11, 9],
            'precip_mean': [100, 1, 1, 1, 1, 100,  # the first value of each row should not be included in the sum (time range of precip)
                            200, 5, 5, 5, 5, 200]
        })
        exp = pd.DataFrame({
            'lat': [49.9] * 2,
            'lon': [-97.2] * 2,
            'datetime': [dt(2021, 1, 8, 0), dt(2021, 1, 9, 0)],
            'agg_day': [0, 0],
            'forecast': [dt(2021, 1, 8, 0), dt(2021, 1, 9, 0)],
            't_max_mean': [22, 21],
            't_min_mean': [11, 9],
            'precip_mean': [4, 20],
        })
        ret = bc.find_aggregate_values(prev_forecasts, date_tm)
        assert_frame_equal(ret, exp, check_like=True)

    def test_find_aggregate_values_first_day_12z(self):
        date_tm = dt(2021, 1, 9, 12)
        prev_forecasts = pd.DataFrame({
            'lat': [49.9] * 12,
            'lon': [-97.2] * 12,
            'datetime': [dt(2021, 1, 8, 6), dt(2021, 1, 8, 12), dt(2021, 1, 8, 18), dt(2021, 1, 9, 0), dt(2021, 1, 9, 6), dt(2021, 1, 9, 12),
                         dt(2021, 1, 9, 6), dt(2021, 1, 9, 12), dt(2021, 1, 9, 18), dt(2021, 1, 10, 0), dt(2021, 1, 10, 6), dt(2021, 1, 10, 12)],
            'forecast': [dt(2021, 1, 7, 12)] * 6 + [dt(2021, 1, 8, 12)] * 6,
            't_max_mean': [500, 500, 19, 22, 500, 500,  # only the third and fourth value of each row should be examined (due to time ranges used to find max temperature)
                           500, 500, 21, 18, 500, 500],
            't_min_mean': [-100, -100, -100, -100, 11, 14,    # only the last values of each row should be examined (time range of minimum temperature)
                           -100, -100, -100, -100, 11, 9],
            'precip_mean': [100, 1, 1, 1, 1, 100, # the first value of each row should not be included in the sum (time range of precip)
                            200, 5, 5, 5, 5, 200]
        })
        exp = pd.DataFrame({
            'lat': [49.9] * 2,
            'lon': [-97.2] * 2,
            'datetime': [dt(2021, 1, 8, 0), dt(2021, 1, 9, 0)],
            'agg_day': [0, 0],
            'forecast': [dt(2021, 1, 7, 12), dt(2021, 1, 8, 12)],
            't_max_mean': [22, 21],
            't_min_mean': [11, 9],
            'precip_mean': [4, 20],
        })
        ret = bc.find_aggregate_values(prev_forecasts, date_tm)
        assert_frame_equal(ret, exp, check_like=True)

    def test_find_aggregate_values_two_day_0z(self):
        date_tm = dt(2021, 1, 10, 0)
        prev_forecasts = pd.DataFrame({
            'lat': [49.9] * 9,
            'lon': [-97.2] * 9,
            'datetime': [dt(2021, 1, 8, 6), dt(2021, 1, 8, 12), dt(2021, 1, 8, 18), dt(2021, 1, 9, 0), dt(2021, 1, 9, 6),
                         dt(2021, 1, 9, 12), dt(2021, 1, 9, 18), dt(2021, 1, 10, 0), dt(2021, 1, 10, 6)],
            'forecast': [dt(2021, 1, 8, 0)] * 9,
            't_max_mean': [500, 500, 19, 22, 500,
                           500, 21, 18, 500],
            't_min_mean': [-100, -100, -100, -100, 11,
                           -10, -100, -100, 9],
            'precip_mean': [100, 1, 1, 1, 1,
                            5, 5, 5, 5]
        })
        exp = pd.DataFrame({
            'lat': [49.9] * 2,
            'lon': [-97.2] * 2,
            'datetime': [dt(2021, 1, 8, 0), dt(2021, 1, 9, 0)],
            'agg_day': [0, 1],
            'forecast': [dt(2021, 1, 8, 0), dt(2021, 1, 8, 0)],
            't_max_mean': [22, 21],
            't_min_mean': [-10, np.NaN],
            'precip_mean': [4, 20],
        })
        ret = bc.find_aggregate_values(prev_forecasts, date_tm)
        assert_frame_equal(ret, exp, check_like=True)

    @pytest.mark.parametrize(
        'biases, counts, correction, exp',
        (
            [
                pd.DataFrame({
                    'bias': [0.5, 1.5, 0.25, 2, 4],
                }),
                pd.DataFrame({
                    'bias': [0.5, 0.5, 1, 0.75, 0.2],
                }),
                'ratio',
                pd.DataFrame({
                    'bias': [0.75, 1.25, 0.25, 1.75, 1.6],
                    'bias_count': [0.5, 0.5, 1, 0.75, 0.2],
                })
            ],
            [
                pd.DataFrame({
                    'bias': [0.5, 1.5, -0.25, -2, 4],
                }),
                pd.DataFrame({
                    'bias': [0.5, 0.5, 1, 0.75, 0.2],
                }),
                'difference',
                pd.DataFrame({
                    'bias': [0.25, 0.75, -0.25, -1.5, 0.8],
                    'bias_count': [0.5, 0.5, 1, 0.75, 0.2],
                })
            ]
        )
    )
    def test_adjust_bias_to_count(self, biases, counts, correction, exp):
        ret = bc.adjust_bias_to_count(biases, counts, correction, 'bias')
        assert_frame_equal(ret, exp, check_like=True)


@pytest.mark.pre_commit
class Test_Pre_Commit:

    def test_true(self):
        assert True


if __name__ == '__main__':
    pytest.main()
