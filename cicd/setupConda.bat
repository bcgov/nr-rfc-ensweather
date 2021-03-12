SET curDir=%cd%
SET minicondaInstallDir=%curDir%\miniconda
SET minicondaInstallFile=miniconda_installer.zip
SET minicondaInstallerFullPath=%minicondaInstallDir%\%minicondaInstallFile%
SET minicondaURL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe


if NOT EXIST %minicondaInstallDir% (
    mkdir %minicondaInstallDir%
)

if NOT EXIST %minicondaInstallerFullPath% (
    curl %minicondaURL% -o %minicondaInstallerFullPath%
)

if NOT EXISTS %minicondaInstallDir%\condabin (
    cd %minicondaInstallDir%
    .\%minicondaInstallFile% /S /InstallationType=JustMe AddToPath=0 /RegisterPython=0 /D=%minicondaInstallDir%
    cd ..
)


@REM To run the the Windows installer for Miniconda in silent mode, use the /S argument. The following optional arguments are supported:
@REM     /InstallationType=[JustMe|AllUsers]---Default is JustMe.
@REM     /AddToPath=[0|1]---Default is 0
@REM     /RegisterPython=[0|1]---Make this the system's default Python. 0 indicates JustMe, which is the default. 1 indicates AllUsers.
@REM     /S---Install in silent mode.
@REM     /D=<installation path>---Destination installation path. Must be the last argument. Do not wrap in quotation marks. Required if you use /S.

@REM All arguments are case-sensitive.

@REM EXAMPLE: The following command installs Miniconda for the current user without registering Python as the system's default:

@REM start /wait "" Miniconda3-latest-Windows-x86_64.exe /InstallationType=JustMe /RegisterPython=0 /S /D=%UserProfile%\Miniconda3

