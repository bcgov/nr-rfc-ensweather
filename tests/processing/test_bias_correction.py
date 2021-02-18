from datetime import datetime as dt
import pytest
import sys
import os
base = '/'.join(__file__.split('/')[:-3])
if base not in sys.path:
    sys.path.append(base)

import pandas as pd
from pandas.testing import assert_frame_equal

from src.processing import bias_correction as bc
import src.config.variable_settings as vs


@pytest.mark.integration
class Test_Integration:

    def test_true(self):
        assert True


@pytest.mark.unit
class Test_Unit:

    def test_true(self):
        assert True

    def test_calculate_biases(self):
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
        assert_frame_equal(ret, exp)

    def test_attach_station_ids(self):
        forecasts = pd.DataFrame({
            'lon': [-112, -114, -115],
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
        })
        ret = bc.attach_station_ids(forecasts, stations)
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
            'lat': [49.9] * 10,
            'lon': [-97.2] * 10,
            'datetime': [dt(2021, 1, 8, 6), dt(2021, 1, 8, 12), dt(2021, 1, 8, 18), dt(2021, 1, 9, 0), dt(2021, 1, 9, 6),
                         dt(2021, 1, 9, 6), dt(2021, 1, 9, 12), dt(2021, 1, 9, 18), dt(2021, 1, 10, 0), dt(2021, 1, 10, 6)],
            'forecast': [dt(2021, 1, 8, 0), dt(2021, 1, 8, 0), dt(2021, 1, 8, 0), dt(2021, 1, 8, 0), dt(2021, 1, 8, 0),
                         dt(2021, 1, 9, 0), dt(2021, 1, 9, 0), dt(2021, 1, 9, 0), dt(2021, 1, 9, 0), dt(2021, 1, 9, 0)],
            't_max_mean': [500, 500, 19, 22, 500,  # only the third and fourth value of each row should be examined (due to time ranges used to find max temperature)
                           500, 500, 21, 18, 500],
            't_min_mean': [-100, -100, -100, -100, 11,    # only the last values of each row should be examined (time range of minimum temperature)
                           -100, -100, -100, -100, 9],
            'precip_mean': [100, 1, 1, 1, 1,  # the first value of each row should not be included in the sum (time range of precip)
                            200, 5, 5, 5, 5]
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
            'lat': [49.9] * 10,
            'lon': [-97.2] * 10,
            'datetime': [dt(2021, 1, 8, 6), dt(2021, 1, 8, 12), dt(2021, 1, 8, 18), dt(2021, 1, 9, 0), dt(2021, 1, 9, 6),
                         dt(2021, 1, 9, 6), dt(2021, 1, 9, 12), dt(2021, 1, 9, 18), dt(2021, 1, 10, 0), dt(2021, 1, 10, 6)],
            'forecast': [dt(2021, 1, 7, 12), dt(2021, 1, 7, 12), dt(2021, 1, 7, 12), dt(2021, 1, 7, 12), dt(2021, 1, 7, 12),
                         dt(2021, 1, 8, 12), dt(2021, 1, 8, 12), dt(2021, 1, 8, 12), dt(2021, 1, 8, 12), dt(2021, 1, 8, 12)],
            't_max_mean': [500, 500, 19, 22, 500,  # only the third and fourth value of each row should be examined (due to time ranges used to find max temperature)
                           500, 500, 21, 18, 500],
            't_min_mean': [-100, -100, -100, -100, 11,    # only the last values of each row should be examined (time range of minimum temperature)
                           -100, -100, -100, -100, 9],
            'precip_mean': [100, 1, 1, 1, 1,  # the first value of each row should not be included in the sum (time range of precip)
                            200, 5, 5, 5, 5]
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
            'forecast': [dt(2021, 1, 8, 0), dt(2021, 1, 8, 0), dt(2021, 1, 8, 0), dt(2021, 1, 8, 0), dt(2021, 1, 8, 0),
                         dt(2021, 1, 8, 0), dt(2021, 1, 8, 0), dt(2021, 1, 8, 0), dt(2021, 1, 8, 0)],
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
            't_min_mean': [-10, 9],
            'precip_mean': [4, 20],
        })
        ret = bc.find_aggregate_values(prev_forecasts, date_tm)
        assert_frame_equal(ret, exp, check_like=True)


@pytest.mark.pre_commit
class Test_Pre_Commit:

    def test_true(self):
        assert True


if __name__ == '__main__':
    pytest.main()
