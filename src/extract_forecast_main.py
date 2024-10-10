from datetime import datetime as dt, timedelta
from downloads import download_models
from processing import extract_model_data
import argparse
import time
import pandas as pd
import os

from common.helpers import get_stations, send_to_objstore, get_from_objstore
from config import general_settings as gs
from config import model_settings as ms
from config import variable_settings as vs

def format_CMC_GRIB_TXT(date_tm):
    file_list = []
    output_dir = date_tm.strftime(f'{gs.DIR}/TXT/combined/%Y%m%d%H/')
    for model in ms.models:
        txt_dir = date_tm.strftime(f'{gs.DIR}/TXT/{model}/%Y%m%d%H/')
        if not os.path.isdir(txt_dir):
            os.makedirs(txt_dir)
            get_from_objstore(txt_dir)
        file_list.append(os.listdir(txt_dir))
    file_list_intersect = list(set(file_list[0]) & set(file_list[1]))

    stations = get_stations()
    stns_per_file = 100
    lats = stations['latitude'].astype('str')
    lons = (stations['longitude']+360).astype('str')

    for file in file_list_intersect:
        first = True
        for model in ms.models:
            txt_dir = date_tm.strftime(f'{gs.DIR}/TXT/{model}/%Y%m%d%H/')
            if first == True:
                data = pd.read_csv(os.path.join(txt_dir,file), header=None)
                first = False
            else:
                data = pd.concat([data,pd.read_csv(os.path.join(txt_dir,file), header=None)])
        data.dropna(inplace=True)
        split_fname = file.split('.')
        N = int(split_fname[0][-1])
        N_i = (N-1)*stns_per_file
        output_string = ''
        for row in range(len(data.index)):
            output_string = output_string + '1:0'
            for col in range(len(data.columns)):
                output_string = output_string + ':lon=' + lons[N_i+col] + ',lat=' + lats[N_i+col] + ',val=' + str(round(data.iloc[row,col],3))
            output_string = output_string + os.linesep
        
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        outfile = split_fname[0] + '.txt'
        with open(os.path.join(output_dir,outfile), "w") as text_file:
            text_file.write(output_string)
    send_to_objstore(output_dir)
        
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download and process ensemble data')
    parser.add_argument('model', choices = ['reps','geps'], type=str)
    args = parser.parse_args()

    start = time.time()
    current_date = dt.now() - timedelta(days=1)
    latest_run = current_date.replace(hour=12)
    download_models.main(args.model, latest_run)
    extract_model_data.main(latest_run, args.model)
    #download_models.main('reps', latest_run)
    #extract_model_data.main(latest_run, 'reps')

    if args.model=='geps':
        format_CMC_GRIB_TXT(latest_run)
    end = time.time()
    time_taken = (end - start)
    print(f'total run time = {time_taken} s')
