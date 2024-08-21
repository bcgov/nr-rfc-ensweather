from datetime import datetime as dt, timedelta
from downloads import download_models
from processing import extract_model_data
import time


#baseline: 262.8 s
#With small_grib: 41.7 s
if __name__ == '__main__':
    start = time.time()
    current_date = dt.now()
    latest_run = current_date.replace(hour=12)
    download_models.main('reps', latest_run)
    #download_models.main('geps', latest_run)

    extract_model_data.main(latest_run, 'reps')
    #extract_model_data.main(latest_run, 'geps')
    end = time.time()
    time_taken = (end - start)
    print(f'total run time = {time_taken} s')
