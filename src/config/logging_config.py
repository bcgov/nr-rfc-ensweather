LOGGING_CONFIG = { 
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': { 
        'standard': { 
            'format': '%(asctime)s [%(levelname)s] %(name)s {%(module)s:%(lineno)d} : %(message)s'
        },
    },
    'handlers': { 
        'default': { 
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
    },
    'loggers': { 
        '': {  # root logger
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'ens_processing': { 
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'processing.bias_correction': { 
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'processing.regrid_model_data': { 
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'common.helpers': { 
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'downloads.download_models': { 
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
        '__main__': {  # if __name__ == '__main__'
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
    } 
}