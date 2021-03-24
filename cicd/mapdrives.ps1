#----------------------------------------------
#
# maps the $ENS_DRIVEMAPPING drive letter to the 
# path described in $NS_NETWORK_DRIVE if V is not
# already mapped
#
#----------------------------------------------
$driveLetters = (Get-PSDrive -PSProvider FileSystem).Root
$mappingWithExtras = $env:ENS_DRIVEMAPPING + ":\"
echo $mappingWithExtras is the drive
if (-Not ($driveLetters -contains $mappingWithExtras)) {
    echo $env:ENS_DRIVEMAPPING + ":\ not there"
    New-PSDrive -Persist -Name "$env:ENS_DRIVEMAPPING" -Root "$env:ENS_NETWORK_DRIVE" -PSProvider "FileSystem"
}
