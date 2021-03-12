
SET curDir=%cd%
SET cygdir=%curDir%\cygdir
SET cygdirbin=%cygdir%\bin
SET cygpackages=%curDir%\cygpackages
SET cygSetup=%cygpackages%\setup_cygwin.exe

if NOT EXIST %cygdir% (
    mkdir %cygdir%
)
if NOT EXIST %cygpackages% (
    mkdir %cygpackages%
)
if NOT EXIST %cygSetup% (
    curl http://cygwin.com/setup-x86_64.exe -o %cygSetup%
)


if NOT EXIST %cygdirbin%/bash.exe (
    %cygSetup% ^
    --quiet-mode ^
    --no-desktop ^
    --download ^
    --local-install ^
    --site http://muug.ca/mirror/cygwin/ ^
    --local-package-dir $cygpackages ^
    --root $cygdir ^
    --no-admin ^
    --no-startmenu ^
    --disable-buggy-antivirus ^
    --packages awk,unzip,lynx,wget,curl,nano,gzip,bzip,cygport,libgomp1,zlib,libgfortran5
)

