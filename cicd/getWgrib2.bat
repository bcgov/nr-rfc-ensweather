SET curDir=%cd%
SET wgrib2Folder=%curDir%\wgrib2
SET wgrib2tarball=%wgrib2Folder%\wgrib2.tgz
SET wgribInstallLocation=%cygwinhome%\bin\wgrib2.exe
SET wgribURL=https://github.com/franTarkenton/wgrib2-Cygwin-Build/suites/2191901122/artifacts/45212649
https://github.com/franTarkenton/wgrib2-Cygwin-Build/suites/2191901122/artifacts/45212649
SET PATH=%cygwinhome%\bin;%PATH%

if NOT EXIST %wgrib2Folder% (
    mkdir %wgrib2Folder%
)


if NOT EXIST %wgribInstallLocation% (
    if NOT EXIST %wgrib2tarball% (
        curl %wgribURL% -o %wgrib2tarball%
    )

)


SET PERSONAL_TOKEN=f64cb00011bd57ba1f8614014e0ffa98c8418baa
SET USER=franTarkenton
SET REPO=wgrib2-Cygwin-Build
-u "$USER:$PERSONAL_TOKEN"
-H "Authorization: token $PERSONAL_TOKEN" \ 


curl \
-u $USER:$PERSONAL_TOKEN \ 
https://api.github.com/repos/franTarkenton/wgrib2-Cygwin-Build/actions/artifacts/45212649

curl -sL https://api.github.com/repos/$USER/$REPO/actions/workflows/build.yml/runs | jq -r '.workflow_runs[0].id?'

curl -L $wgribURL --output "./junk.zip"



curl \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/octocat/hello-world/actions/artifacts/42/ARCHIVE_FORMAT

-H "Accept: application/vnd.github.v3+json" \

curl  \
-H "Authorization: token $PERSONAL_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
https://api.github.com/repos/$USER/$REPO/actions/artifacts/45212649

curl  \
-v \
-H "Authorization: token $PERSONAL_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
https://api.github.com/repos/franTarkenton/wgrib2-Cygwin-Build/actions/artifacts/45212649/zip

curl  \
-v \
-H "Authorization: token $PERSONAL_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
 https://pipelines.actions.githubusercontent.com/8deaILM7pEGxbtnVn5owwpM2EooYTftSr7cxEIE3INZrc2PDem/_apis/pipelines/1/runs/16/signedartifactscontent?artifactName=wgrib2-cygwin-binary&urlExpires=2021-03-12T21%3A28%3A44.4471922Z&urlSigningMethod=HMACV1&urlSignature=10R4%2FMdqY3gshwrNwWdlJ86SNDNhfBfXloontTR5B0U%3D

curl \
  https://api.github.com/repos/octocat/hello-world/actions/artifacts/42