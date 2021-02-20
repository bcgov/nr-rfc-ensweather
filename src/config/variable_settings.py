import numpy as np

metvars = {
    'precip': {
        'mod': {
            'geps': ['APCP_SFC_0', 'APCP', 'surface'],
        },
        'ensemble_percentiles': [25, 75],
        'utc_time_start': 6,  # 6 hours after 0z run
        'time_range_length': 24,  # 24 hour sum
        'expected_values': 4,
        'aggregate_function': np.sum,
        'unit_offset': 0,
        'mult': None,
        'units': 'millimetres',
        'correction': 'ratio',
    },
    't_max': {
        'mod': {
            'geps': ['TMAX_TGL_2m', 'TMAX', '2 m above ground'],
        },
        'ensemble_percentiles': [25, 75],
        'utc_time_start': 12,  # 12 hours after 0z run
        'time_range_length': 12,  # morning to evening max
        'expected_values': 2,
        'aggregate_function': np.max,
        'unit_offset': 273.15,
        'units': 'celsius',
        'correction': 'difference',
    },
    't_min': {
        'mod': {
            'geps': ['TMIN_TGL_2m', 'TMIN', '2 m above ground'],
        },
        'ensemble_percentiles': [25, 75],
        'utc_time_start': 24,  # 24 hours after 0z run
        'time_range_length': 12, # evening to next morning min
        'expected_values': 2,
        'aggregate_function': np.min,
        'unit_offset': 273.15,
        'units': 'celsius',
        'correction': 'difference',
    },
}


# old stuff
'''
    't': {
        'mod': {
            'rdps': ['TMP_TGL_2', 'TMP', '2 m above ground'],
            'gdps': ['TMP_TGL_2', 'TMP', '2 m above ground'],
            'reps': ['TMP_TGL_2m', 'TMP', '2 m above ground'],
            'geps': ['TMP_TGL_2m', 'TMP', '2 m above ground'],
            'nam': [None, 'TMP', '2 m above ground'],
            'rap': [None, 'TMP', '2 m above ground'],
            'gfs': [None, 'TMP', '2 m above ground'],
            'sref': [None, 'TMP', '2 m above ground'],
            'gefs': [None, 'TMP', '2 m above ground'],
            'met_fr': ['TMP/2m', 'TMP', '2 m above ground'],
            'icon': ['t_2m', 'TMP', '2 m above ground'],
        },
        'acc': False,
        'weighted': True,
        'corrected': True,
        'interpolation': 'distance weighted',
        'ensemble_percentiles': [25, 75],
        'unit_offset': 273.15,
        'dp': 1,
        'offset': None,
        'std': True,
        'mult': None,
        'units': 'celsius',
        'scale': 10,
        'db_name': 'tmpc',
        'smF': None,
        'neg': False,
    },

'''