# Deployment

Describes how the deployment / running of the ens processing scripts is going to work

## Requirements:

### WGRIB2

A github repository and assoicated action has been created that:
* installs cygwin 
* compiles the wgrib2 using cygwin
* zips the results and makes available via a action artifact

binary that can be executed using github actions:

https://github.com/franTarkenton/wgrib2-Cygwin-Build


