#! /bin/bash

path=../mocde/results/history/$1
#mocde=mocde-randbest1-1.0-0.1
mocde=mocde
#report=AAA
#functions="zdt1"
report=report-$1
functions="zdt* dtlz*"
#functions="zdt* dtlz* uf*"
id="extres"

#./src/analyze.py -R $report --results $path/$mocde $path/moead $path/paes $path/nsga2 --functions $functions #-hl $mocde
./src/analyze.py -R report-zdt-$1 --results $path/$mocde $path/nsga2 $path/moead $path/paes --functions "zdt*" -id $id
./src/analyze.py -R report-dtlz-$1 --results $path/$mocde $path/nsga2 $path/moead $path/paes --functions "dtlz*" -id $id
