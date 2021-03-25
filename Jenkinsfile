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
        stage('run script') {
            bat '''
                echo running script
            '''
        }
    }
}




