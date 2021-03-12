SET curDir=%cd%
SET minicondaInstallDir=%curDir%\miniconda
SET minicondaBin=%minicondaInstallDir%\condabin
SET condaEnvPath=%curDir%\rfc_conda_envs
SET ensweatherCondaPath=%condaEnvPath%\ens_weather

SET PATH=%minicondaBin%;%PATH%


if NOT EXIST %condaEnvPath% (
    mkdir %condaEnvPath%
)
if NOT EXIST %ensweatherCondaPath% (
    mkdir %ensweatherCondaPath%
)
if NOT EXIST %ensweatherCondaPath%\python.exe (
    ::cd %WORKSPACE%
    conda.bat env create --prefix %ensweatherCondaPath% --file %WORKSPACE%\environment.yaml
)
