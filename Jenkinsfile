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
    }
}
