:: creates a conda env in the folder
:: %rfc_conda_envs%
SET curDir=%cd%
SET minicondaInstallDir=%curDir%\miniconda
SET minicondaBin=%minicondaInstallDir%\condabin

::SET condaEnvPath=%curDir%\rfc_conda_envs
::SET ensweatherCondaPath=%condaEnvPath%\ens_weather

SET PATH=%minicondaBin%;%PATH%


if NOT EXIST %condaEnvPath%\python.exe (
    ::cd %WORKSPACE%
    conda.bat env create --prefix %condaEnvPath% --file %condaEnvFilePath%
)
