SET curDir=%cd%
SET wgrib2Folder=%curDir%\wgrib2
SET wgrib2tarball=%wgrib2Folder%\wgrib2.tgz
SET wgrib2TarOutFolder=%wgrib2Folder%\grib2
SET wgribInstallLocation=%cygwinhome%\bin\wgrib2.exe
@REM Doesnt seem like it is possible do download artifacts outside of the ui.
SET wgribURL=https://github.com/franTarkenton/wgrib2-Cygwin-Build/releases/download/20210313-0003/wgrib-cyg.tgz
SET PATH=%cygwinhome%\bin;%PATH%

if NOT EXIST %wgrib2Folder% (
    mkdir %wgrib2Folder%
)


if NOT EXIST %wgribInstallLocation% (
    if NOT EXIST %wgrib2tarball% (
        curl -L -H "Accept"="application/json" %wgribURL% -o %wgrib2tarball%
    )
    if not EXIST %wgrib2TarOutFolder% (
        cd %wgrib2Folder%
        bash -c "gunzip < $wgrib2tarball | tar -xf - "
        cd %curDir%
    )
    copy %wgrib2TarOutFolder%\wgrib2\wgrib2.exe %wgribInstallLocation%

)

