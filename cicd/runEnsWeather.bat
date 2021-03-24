@REM ------------------------------------
@REM Needs the following environment variables
@REM - ENS_ARTIFACTS - Where downloaded data will reside
@REM - CYGWINHOME
@REM - ENS_CONDA_ENV - The path to the conda environent used by
@REM                   the ens weather run
@REM - ENS_WEATHER_DATA - where the data will be located after 
@REM                   processing is complete
@REM ------------------------------------

@REM -------- set up the path --------
SET PATH=%CYGWINHOME%\bin;%CONDABIN%;%PATH%
SET WGRIB2EXEC=%CYGWINHOME%\bin\wgrib2.exe

@REM -------- activate the conda env --------
conda.bat activate %condaEnvPath%

@REM -------- run the ens weather --------
%condaEnvPath%\python src\ens_processing.py -V

