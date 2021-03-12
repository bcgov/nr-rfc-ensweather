SET curDir=%cd%
SET pyinstallDir=%curDir%\python
SET pythoninstaller=python39_installer.zip
SET pythoninstallerFullPath=%pyinstallDir%\%pythoninstaller%
SET pythonexeFullPath=%pyinstallDir%\python.exe
SET PATH=%cygwinhome%\bin;%PATH%

@REM needs cygwinhome

:: ---- debugging -----
if EXIST %pyinstallDir% (
    del /F /Q %pyinstallDir%
    rmdir /Q %pyinstallDir%
)


if NOT EXIST %pyinstallDir% (
    mkdir %pyinstallDir%
)
if NOT EXIST %pythoninstallerFullPath% (
    curl https://www.python.org/ftp/python/3.9.2/python-3.9.2-embed-amd64.zip -o %pythoninstallerFullPath%
)
if NOT EXIST %pythonexeFullPath% (
    cd %pyinstallDir%
    dir
    echo unzipping the python file    
    %cygwinhome%\bin\bash.exe -c "unzip $pythoninstaller && chmod +x *"
    %cygwinhome%\bin\bash.exe -c "echo 'import site' >> python39._pth"
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py"
    echo running getpip
    %pythonexeFullPath% get-pip.py
    echo done
)
