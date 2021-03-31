# Deployment

Describes how the deployment / running of the ens processing scripts is working when deployed to jenkins

## Env Vars used by Jenkins

* **RFC_ARTIFACTS_FOLDER** - location where the ens weather artifacts will be located
   under this folder the following folders will be created:

  * **cygdir**         - The cygwinhome
  * **cygpackages**    - where cygwin install packages will get cached
  * **python**         - embedded python3 install
  * **wgrib2**         - where wgrib2 will get downloaded to
  * **miniconda**      - miniconda install location
  * **rfc_conda_envs** - home for the various conda environments used by river forecast centre data processing scripts
* **ENS-WEATHER-DATA** - location of any data downloaded or otherwise used by the ensemble weather processing scripts
* **GIT_REPOSITORY**   - https path to the git repository with the rfc ensemble weather code.
* **TAGNAME**          - Branch/release tag to run
* **ENS_DRIVEMAPPING** - drive letter to be used for the river forecast centres share
* **ENS_NETWORK_DRIVE**- the network share (unc), this share will be connected to $ENS_DRIVEMAPPING
* **ENS_WEATHER_DATA** - file path to where the output data created by the ensemble weather scripts will be located.

## Jenkins Steps:

### Checkout
* Gets the code from the git repo
* currently git integration in jenkins cron seems to be broken so getting this with clone / checkout / pull in windows bat steps




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




