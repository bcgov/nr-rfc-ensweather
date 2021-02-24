# BC FORECASTING
This project was designed by Weatherlogics for the use of the B.C. government for the purposes of bias correcting and forecasting for individual stations run by the B.C. government using the GEPS model.

## Install

### Project installation

Within the project directory, the anaconda environment used by this project can be installed as follows:

```
conda env create --file environment.yaml
```

If anaconda or miniconda is not already installed on the machine in which this program runs, it is recommended to install miniconda so as to reduce overhead. Miniconda installation instructions can be found on the anaconda website.

### WGRIB2 Installation
An additional package must be installed for the project to function correctly (wgrib2). This is an ncep package used for the purposes of modifying and reading grib files used to store government forecast models.

In a suitable directory (downloads for example):

```
wget ftp://ftp.cpc.ncep.noaa.gov/wd51we/wgrib2/wgrib2.tgz
tar -xzvf wgrib2.tar

cd grib2
sed 's/\\#/#/' <makefile >makefile.cygwin

export CC=gcc
export FC=gfortran
make

cp wgrib2/wgrib2.exe C:\Program Files\wgrib2
```
Modifications may need to be made to the above script in order to deal with different operating systems. However, installation instructions for this package are also provided by ncep at the same site from which wgrib2 is downloaded.

## Usage
### Daily Runs
Daily runs are designed to be run on a schedule, however the program can be run manually, if that is required.

Using a terminal, change directories to the root of the bc_forecasting directory, and type in the following commands.
```
conda activate bc_forecasting
python src/ens_processing.py
```

Arguments can be used to change the behaviour of the run. These can be seen with the following.

```
conda activate bc_forecasting
python src/ens_processing.py -h
```

### Settings Configuration

Before first usage, in src/config/general_settings:
- DIR will need to point to the root directory of the project.
- WGRIB2 must be set to the location of the WGRIB2 install. In the WGRIB2 script found above, this location is 'C:\Program Files\wgrib2'

Beyond that, the user may choose to adjust BIAS_DAYS to include more or fewer days in the bias correction, and may also adjust MAX_HOURS if they wish to reduce the number of days in which to forecast. MAX_HOURS could also be increased if the GEPS model increased in it's runtime.

### New Stations

Within the resources folder, the stations csv contains all stations for which a forecast is created. To add a new station, simply fill in the required fields in this csv. The entered station must also be found in the observational data sheet in order to be used.

### Output

Two excel files are created as output of the bias correction program. One is placed in output/daily_raw, the other in output/forecasts. Both are named by their creation date (yyyy-mm-dd.xlsx).
The daily raw file contains a sheet for each station, with each variable present as a mean value, lower percentile and upper percentile forecast.
The forecast file contains all stations on a single sheet, with only the mean value present.