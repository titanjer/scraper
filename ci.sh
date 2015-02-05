#!/bin/bash
source $VIRTUAL_ENV/bin/activate

echo "[INFO] Running pep8"
pep8 --first --select E,W scraper
echo "[INFO] Running lint"
for init_file in `find scraper -name '__init__.py'`
do
    module=`dirname $init_file`
    echo "[INFO] Linting $module"
    pylint $module
done
