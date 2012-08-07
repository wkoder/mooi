# /bin/bash

path=../mocde/results/history/$1
name=mocde-randbest1
main=$name-1.0-0.1

./src/analyze.py -R report-internal-$1 --results $path/$main $path/$name-1.0-0.2 --functions "*" -hl $main
