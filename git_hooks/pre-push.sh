#!/bin/sh
# Redirect output to stderr
exec 1>&2
pytest
if [ $? -ne 0 ]
then
echo 'Failed tests'
exit 1
fi
