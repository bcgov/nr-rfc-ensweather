# BC FORECASTING
This project was designed by Weatherlogics for the use of the B.C. government for the purposes of bias correcting and forecasting for individual stations run by the B.C. government using the GEPS (Global Ensemble Prediction System).

## Install

Installation of this program involves two main parts: installing the python dependencies and installing wgrib2. We recommend installing the python dependences by creating a conda environment as described below. Wgrib2 is a program used to process GRIB2 files containing meteorological data. It must be downloaded and then compiled. We have included some basic instructions about this process below, but more information about wgrib2 is available from the software developer.

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

More details and tips for compiling wgrib2 are available at: https://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/

## Configuration

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

## Usage

The ensemble processing script is executed from the command line. To start a run, the user activates their conda environment and then executes the python script. In its simplest form, the script is executed without any arguments to process the latest GEPS forecast. However, there are some arguments available to control the program:

usage: python src/ens_processing.py [-h] [-v] [-V] [-r RUN] [-d] [-p]

Main program for ensemble model processing.

optional arguments:
  -h, --help         show this help message and exit
  -v, --version      show program's version number and exit
  -V, --verbose      Do not silence terminal output.
  -r RUN, --run RUN  Specify run to forecast.
  -d, --download     Only download, do not process.
  -p, --process      Only process, do not download.

## Examples
The program can be run on a schedule (e.g. using cron), or executed manually. Here is an example of running all aspects of the program for the most recent cycle of the GEPS.

Using a terminal, change directories to the root of the bc_forecasting directory, and type in the following commands.
```
conda activate bc_forecasting
python src/ens_processing.py
```

Arguments can be used to change the behaviour of the run. For example, here we specify a previous cycle of the GEPS to process.

```
conda activate bc_forecasting
python src/ens_processing.py -r 20210220_00
```

Arguments can also be used to only download or process the GEPS. For example, if the GEPS for the current cycle has already been downloaded and we only want to process it:

```
conda activate bc_forecasting
python src/ens_processing.py -p
```

Or if the GEPS for a previous cycle has already been downloaded and we only want to process it:

```
conda activate bc_forecasting
python src/ens_processing.py -p -r 20210220_00
```

## Bias Correction

### How it works
Using station observational data and archived historical forecasts, we can calculate the errors made by the forecasted data over a period of time. Analyzing those errors may show a systemic bias in the forecast (temperature consistently too low for instance), and using the calculated errors, we then adjust the forecast by the average calculated error. If observations or forecasts are missing for some portion of the bias correction daily range, the bias correction is reduced in magnitude. For example, if only one day of data is present, and the bias range is fifteen days. If that single day had an error of +15 temperature, the bias it generated would be reduced to 1/15 of the original error. (+15 degrees) * (one available day / expected available days).
For ratio type bias correction such as precip, a time range of values is summed for both observations and forecasts. The ratio of these values (forecasts/observations) is then used as a multiplier for the new forecast. For example, if forecasts predicted 40mm of precipitation over a time period, and only 20mm occurred, the multiplier would be 0.5 for the new forecast.