from datetime import datetime as dt, timedelta
from downloads import download_models
from processing import extract_model_data
import argparse
import time


#baseline: 262.8 s
#With small_grib: 41.7 s
# run 1: 170 s
# run 2: 105 s
# run 3: 101 s (Pool instead of thread pool)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download and process ensemble data')
    parser.add_argument('model', choices = ['reps','geps'], type=str, required=True)
    args = parser.parse_args()
    
    start = time.time()
    current_date = dt.now()
    latest_run = current_date.replace(hour=12)
    download_models.main(args.model, latest_run)
    #download_models.main('geps', latest_run)

    extract_model_data.main(latest_run, args.model)
    #extract_model_data.main(latest_run, 'geps')
    end = time.time()
    time_taken = (end - start)
    print(f'total run time = {time_taken} s')
