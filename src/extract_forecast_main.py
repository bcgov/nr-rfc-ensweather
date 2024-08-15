from datetime import datetime as dt, timedelta
from downloads import download_models
from processing import extract_model_data

if __name__ == '__main__':
    current_date = dt.now()
    latest_run = current_date.replace(hour=12)
    download_models.main('reps', latest_run)
    download_models.main('geps', latest_run)
    extract_model_data.main(latest_run, 'reps')
    extract_model_data.main(latest_run, 'geps')
