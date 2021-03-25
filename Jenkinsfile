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
        stage('build') {
            build job: 'ensemble_weather_build',
            parameters: [
                string(name: 'TAGNAME', value: "${TAGNAME}"), 
                string(name: 'no_proxy', value: "${no_proxy}"), 
                string(name: 'RFC_ARTIFACTS_FOLDER', value: "${RFC_ARTIFACTS_FOLDER}"), 
                string(name: 'ENS_NETWORK_DRIVE', value: "${ENS_NETWORK_DRIVE}"), 
                string(name: 'ENS_DRIVEMAPPING', value: "${ENS_DRIVEMAPPING}"), 
                string(name: 'ENS_WEATHER_DATA', value: "${ENS_WEATHER_DATA}")]
        }
        stage('prepClimateObsData') {
            bat '''
                SET CONDABIN=%RFC_ARTIFACTS_FOLDER%\\miniconda\\condabin
                SET condaEnvPath=%RFC_ARTIFACTS_FOLDER%\\rfc_conda_envs\\nr-rfc-ensweather
                call conda.bat activate %condaEnvPath%
                SET PATH=%CYGWINHOME%\bin;%CONDABIN%;%PATH%
                echo %%
                %condaEnvPath%\\python src\\extractClimateObservations.py
            '''
        }
        stage('run script') {
            bat '''
                echo running script
                :: ----- run ens weather ------
                echo setting up ens weather run
                SET CYGWINHOME=%RFC_ARTIFACTS_FOLDER%\\cygdir
                SET CONDABIN=%RFC_ARTIFACTS_FOLDER%\\miniconda\\condabin
                SET condaEnvPath=%RFC_ARTIFACTS_FOLDER%\\rfc_conda_envs\\nr-rfc-ensweather
                SET ENS_HOME=%WORKSPACE%

                @REM .\\cicd\\runEnsWeather.bat
                SET PATH=%CYGWINHOME%\bin;%CONDABIN%;%PATH%
                SET WGRIB2EXEC=%CYGWINHOME%\\bin\\wgrib2.exe

                @REM -------- activate the conda env --------
                call conda.bat activate %condaEnvPath%

                @REM -------- run the ens weather --------
                %condaEnvPath%\\python src\\ens_processing.py

                echo completed run
            '''
        }
    }
}
