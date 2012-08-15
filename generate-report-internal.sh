# /bin/bash

path=../mocde/results/history/$1
name=mocde
main=$name-L0
#functions="zdt* dtlz*"
functions="zdt4"
id="intres"

#./src/analyze.py -R report-internal-$1 --results $path/$name-L10 $path/$name-L20 $path/$name-L50 $path/$main --functions $functions #-hl $main
./src/analyze.py -R report-internal-zdt-$1 --results $path/$main $path/$name-L50 $path/$name-L20 $path/$name-L10 --functions "zdt*" -id $id
./src/analyze.py -R report-internal-dtlz-$1 --results $path/$main $path/$name-L50 $path/$name-L20 $path/$name-L10 --functions "dtlz*" -id $id
