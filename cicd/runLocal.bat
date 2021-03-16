@REM -----------------------
@REM  
@REM   To facilitate debugging process this 
@REM   script will run the full jenkins flow local to 
@REM   a specific machine
@REM  
@REM -----------------------

SET CURDIR=%cd%
SET RFC_ARTIFACTS_FOLDER=C:\Kevin\proj\rfc-ensweather\cicd\artifacts
SET RFC_CONDA_ENV=%RFC_ARTIFACTS_FOLDER%\rfc_conda_envs\cicd\ens_weather

@REM  cygwin install
@REM ------------------------
cd %RFC_ARTIFACTS_FOLDER%
.\cicd\setupConda.bat
cd %CURDIR%

@REM get conda
@REM ------------------------
cd %RFC_ARTIFACTS_FOLDER%
.\cicd\getConda.bat
cd %CURDIR%

@REM build conda env 
@REM ------------------------
cd %RFC_ARTIFACTS_FOLDER%
if not exist %RFC_CONDA_ENV% (
    mkdir %RFC_CONDA_ENV%
)
SET condaEnvFilePath=%CURDIR%/environment.yaml
SET condaEnvPath=%RFC_CONDA_ENV%
.\setupConda.bat
cd %CURDIR%

@REM RUN the Script 
@REM ------------------------
SET CYGWINHOME=%RFC_ARTIFACTS_FOLDER%\cygdir
SET CONDABIN=%RFC_ARTIFACTS_FOLDER%\miniconda\condabin
SET condaEnvPath=%RFC_ARTIFACTS_FOLDER%\rfc_conda_envs\ens_weather
SET ENS_HOME=%CURDIR%
SET ENS_WEATHER_DATA=C:\Kevin\proj\rfc-ens-data

@REM .\cicd\runEnsWeather.bat
SET PATH=%CYGWINHOME%\bin;%CONDABIN%;%PATH%
SET WGRIB2EXEC=%CYGWINHOME%\bin\wgrib2.exe

@REM -------- activate the conda env --------
call conda.bat activate %condaEnvPath%

@REM -------- run the ens weather --------
@REM %condaEnvPath%\python src/ens_processing.py -V

