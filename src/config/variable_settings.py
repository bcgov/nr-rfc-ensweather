import numpy as np

# metvar documentation
'''
    'variable name': {
        'mod': {
            'model': [file name, grib name, grib level]
            'geps': ['APCP_SFC_0', 'APCP', 'surface'],
        },
        'utc_time_start': hours after 0z forecast, # start of time range used to aggregate variable (precip is 6z-6z, so time_start is 6)
        'ensemble_values: The values calculated and stored for future use (do not touch this)
        'ensemble_percentiles': Dictionary of percentiles with a relevant suffix. This can be modified at any time if the user pleases.
        'time_range_length': number of hours used to aggregate variable,  # precip is 6z-6z which is 24 hours
        'expected_values': number of forecast values expected to be used in bias correction, # precip has 4 (12, 18, 24, 6)
        'aggregate_function': aggregate function,
        'unit_offset': constant offset used to correct downloaded data to metric,
        'correction': bias correction type,
    },
'''

funcs = {
    'mean': np.nanmean,
    'max': np.nanmax,
    'min': np.nanmin,
    'median': np.nanmedian,
}

metvars = {
    'precip': {
        'mod': {
            'geps': ['APCP_SFC_0', 'APCP', 'surface'],
        },
        'ensemble_values': ['mean', 'median', 'max', 'min'],
        'percentiles': {
            25: 'lower_percentile',
            75: 'upper_percentile',
        },
        'utc_time_start': 6,  # 6 hours after 0z run
        'time_range_length': 24,  # 24 hour sum
        'expected_values': 4,
        'aggregate_function': np.nansum,
        'unit_offset': 0,
        'correction': 'ratio',
    },
    'temp': {
        'mod': {
            'geps': ['TMP_TGL_2m', 'TEMP', '2 m above ground'],
        },
        'ensemble_values': ['mean', 'median', 'max', 'min'],
        'percentiles': {
            25: 'lower_percentile',
            75: 'upper_percentile',
        },
        'utc_time_start': 12,  # 12 hours after 0z run
        'time_range_length': 12,  # morning to evening max
        'expected_values': 2,
        'aggregate_function': np.nanmax,
        'unit_offset': 273.15,
        'correction': 'difference',
    },
}
