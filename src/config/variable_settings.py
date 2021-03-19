import numpy as np

# metvar documentation
'''
    'variable name': {
        'mod': {
            'model': [file name, grib name, grib level]
            'geps': ['APCP_SFC_0', 'APCP', 'surface'],
        },
        'ensemble_percentiles': [upper percentile, lower percentile], options: [10, 25, 50, 75, 90]
        'utc_time_start': hours after 0z forecast, # start of time range used to aggregate variable (precip is 6z-6z, so time_start is 6)
        'time_range_length': number of hours used to aggregate variable,  # precip is 6z-6z which is 24 hours
        'expected_values': number of forecast values expected to be used in bias correction, # precip has 4 (12, 18, 24, 6)
        'aggregate_function': aggregate function,
        'unit_offset': constant offset used to correct downloaded data to metric,
        'correction': bias correction type,
    },
'''

excel_variable_order = ['t_max', 't_min', 'precip']
suffix_order =  ['mean', 'median', 'max', 'min', 'upper_percentile', 'lower_percentile']

metvars = {
    'precip': {
        'mod': {
            'geps': ['APCP_SFC_0', 'APCP', 'surface'],
        },
        'ensemble_values': {
            'ens mean': '_mean',
            50: '_median',
            25: '_lower_percentile',
            75: '_upper_percentile',
            'max all members': '_max',
            'min all members': '_min',
        },
        'utc_time_start': 6,  # 6 hours after 0z run
        'time_range_length': 24,  # 24 hour sum
        'expected_values': 4,
        'aggregate_function': np.nansum,
        'unit_offset': 0,
        'correction': 'ratio',
    },
    't_max': {
        'mod': {
            'geps': ['TMAX_TGL_2m', 'TMAX', '2 m above ground'],
        },
        'ensemble_values': {
            'ens mean': '_mean',
            50: '_median',
            25: '_lower_percentile',
            75: '_upper_percentile',
            'max all members': '_max',
            'min all members': '_min',
        },
        'utc_time_start': 12,  # 12 hours after 0z run
        'time_range_length': 12,  # morning to evening max
        'expected_values': 2,
        'aggregate_function': np.nanmax,
        'unit_offset': 273.15,
        'correction': 'difference',
    },
    't_min': {
        'mod': {
            'geps': ['TMIN_TGL_2m', 'TMIN', '2 m above ground'],
        },
        'ensemble_values': {
            'ens mean': '_mean',
            50: '_median',
            25: '_lower_percentile',
            75: '_upper_percentile',
            'max all members': '_max',
            'min all members': '_min',
        },
        'utc_time_start': 24,  # 24 hours after 0z run
        'time_range_length': 12, # evening to next morning min
        'expected_values': 2,
        'aggregate_function': np.nanmin,
        'unit_offset': 273.15,
        'correction': 'difference',
    },
}
