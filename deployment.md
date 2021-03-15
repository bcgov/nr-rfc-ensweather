# Deployment

Describes how the deployment / running of the ens processing scripts is going to work

## Env Vars

* **RFC_ARTIFACTS_FOLDER** - location where the ens weather artifacts will be located
   under this folder the following folders will be created:

  * **cygdir**         - The cygwinhome
  * **cygpackages**    - where cygwin install packages will get cached
  * **python**         - embedded python3 install
  * **wgrib2**         - where wgrib2 will get downloaded to
  * **miniconda**      - miniconda install location
  * **rfc_conda_envs** - home for the various conda environments used by river forecast centre data processing scripts
* **ENS-WEATHER-DATA** - location of any data downloaded or otherwise used by the ensemble weather processing scripts




    

* CYGWINBASE     - the root directory for cygwin install
* CYGWINPACKAGES - contains the cached cygwin packages and the location of setup.exe
* ENSWEATHERDATA - Where ensemble weather data will be located
* CONDAENV_ENS   - location of the ens conda environment

## Requirements:

### WGRIB2 - Build

A github repository and assoicated action has been created that:
* installs cygwin 
* compiles the wgrib2 using cygwin
* zips the results and makes available via a action artifact

binary that can be executed using github actions:

https://github.com/franTarkenton/wgrib2-Cygwin-Build

The artifact that is created by the run:
https://github.com/franTarkenton/wgrib2-Cygwin-Build/actions/runs/626329992

Time to build: approx 15-20mins

### WGRIB2 - Deploy / Run

A cygwin build needs to be created with specific dependencies in order to be able
to run the artifact created by the github action.  This can be created by running
the script ./cicd/wgrib2Setup.ps1 script

Download uncompress the wgrib tarball

copy the wgrib2.exe to the cygwin bin directory

### Conda Setup

Create the conda environment
```
conda env create --prefix $CONDAENV_ENS --file environment.yaml
```

Activate the conda environment
conda activate $CONDAENV_ENS




