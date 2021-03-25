node('zavijava_rfc') {
    withEnv([
        "JOB_NAME=EnsembleWeather_build", 
        "TEMP=$WORKSPACE\\tmp",
        "TMP=$WORKSPACE\\tmp",
        "no_proxy=github.com"
        ]) {
        stage('checkout') {
            //sh 'if [ ! -d "$TEMP" ]; then mkdir $TEMP; fi'
            checkout([$class: 'GitSCM', branches: [[name: "${env.TAGNAME}"]], extensions: [], userRemoteConfigs: [[url: 'https://github.com/bcgov/nr-rfc-ensweather']]])
        }
        stage('mapdrives') {
            bat '''
            :: -------- Create RFC Drive Mapping and required folders -------
            echo setting up required directories
            wmic logicaldisk list brief
            whoami

            if NOT EXIST %ENS_DRIVEMAPPING%:\\nul  (
                net use %ENS_DRIVEMAPPING%: %ENS_NETWORK_DRIVE% /PERSISTENT:NO
                @REM powershell -File ./mapdrives.ps1
            )

            IF NOT EXIST %RFC_ARTIFACTS_FOLDER% (
                echo creating the folder %RFC_ARTIFACTS_FOLDER% 
                mkdir %RFC_ARTIFACTS_FOLDER%
            )

            IF NOT EXIST %ENS_WEATHER_DATA% (
                echo creating the folder %ENS_WEATHER_DATA% 
                mkdir %ENS_WEATHER_DATA%
            )
            echo complete
            '''
        }
        stage('setup Cygwin') {
            bat '''
            :: ------- GET/SETup Cygwin --------
            SET curDir=%RFC_ARTIFACTS_FOLDER%
            SET cygdir=%RFC_ARTIFACTS_FOLDER%\cygdir
            SET cygdirbin=%cygdir%\bin
            SET cygpackages=%RFC_ARTIFACTS_FOLDER%\cygpackages
            SET cygSetup=%cygpackages%\setup_cygwin.exe

            echo cygdir %cygdir%
            echo cygdirbin %cygdirbin%
            echo cygpackages %cygpackages%
            echo cygSetup %cygSetup%


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
                --local-package-dir %cygpackages% ^
                --root %cygdir% ^
                --no-admin ^
                --no-startmenu ^
                --disable-buggy-antivirus ^
                --packages awk,unzip,lynx,wget,curl,nano,gzip,bzip,cygport,libgomp1,zlib,libgfortran5
            )
        '''
        }
    }
}
