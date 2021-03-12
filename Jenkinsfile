node('etl-test') {
    withEnv([
        "JOB_NAME=EnsembleWeather_build", 
        "ARTIFACT_DIR=\\drain.dmz\Shared",
        "ENS_DRIVEMAPPING=",
        "ENS_NETWORK_DRIVE=",
        "ENS_ARTIFACTS_FOLDER=$DRIVEMAPPING:\ensemble_weather\build",
        "PYTHON_HOME=$ENS_ARTIFACTS_FOLDER\python",
        "WGRIB2EXEC="
        "IDIRUSER"
        "IDIRPSWD"
        "TEMP=$WORKSPACE\\tmp",
        "TMP=$WORKSPACE\\tmp",
        ]) {
        stage('checkout') {
            sh 'if [ ! -d "$TEMP" ]; then mkdir $TEMP; fi'
            checkout([$class: 'GitSCM', branches: [[name: "${env.TAGNAME}"]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'SubmoduleOption', disableSubmodules: false, parentCredentials: true, recursiveSubmodules: true, reference: '', trackingSubmodules: false]], gitTool: 'Default', submoduleCfg: [], userRemoteConfigs: [[credentialsId: '607141bd-ef34-4e80-8e7e-1134b7c77176', url: 'https://github.com/bcgov/replication_health_check']]])
        }
        stage('map drives') {
            bat '''
                cd cicd
                powershell -File ./mapdrives.ps1
                cd ..
            '''
        }
        stage('build cygwin') {
            // this only happens once.
            bat '''
                IF NOT EXIST %ENS_ARTIFACTS_FOLDER% mkdir %ENS_ARTIFACTS_FOLDER%
                cd %ENS_ARTIFACTS_FOLDER%
                powershell -File %$WORKSPACE%/cicd/setupCygwin
                cd %$WORKSPACE%
            '''
        }
        stage("Getpython") {
            bat '''
            # going to use bash and cygwin to get this done

            '''
            
        }
    stage('build get python') {
        // download the embedded python
        //   curl https://www.python.org/ftp/python/3.9.2/python-3.9.2-embed-amd64.zip -o pythonembed.zip
        // unzip it
        //   unzip pythonembed.zip
        // go into directory
        //   cd python3.9.2
        // Modify the python39._.pth, uncomment the site
        //   echo "import site" >> python39._pth
        // get pip using curl 
        //   curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        // run get pip
        //   
        // add root directory and scripts directory to path
        // run get pip

    }
    stage('conda env conf') {
        // if check existence of a miniconda directory, if not then install
        // https://dev.to/waylonwalker/installing-miniconda-on-linux-from-the-command-line-4ad7

        // create a conda env directory on fileshare
        // install conda env
        //  conda env create --file environment.yaml --prefix $CONDAENVPATH
        //
        // a) make sure cygwin is installed (store somewhere and re-use)
        // b) copy wgrib2 binary to cygwin bin directory
        // c) configure paths (wittle down to required paths, remove git paths as these confuse cygwin, add cygwin bin)
        // d) make sure conda is installed (store somewhere and re-use)
        // e) initiate conda env 
        // f) initiate a cygwin bash shell
        // g) call python script (hopefully the system calls (subprocess) will hit the cygwin processes)
        //


    }
    stage('wgrib install') {
        // check if wgrib exe exists, if not then download source and install
        
    }
    stage('')

}
