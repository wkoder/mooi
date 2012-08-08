#! /bin/bash

path=../mocde/results/history/$1
#mocde=mocde-randbest1-1.0-0.1
mocde=mocde
#report=AAA
#functions="zdt1"
report=report-$1
functions="zdt* dtlz*"
#functions="zdt* dtlz* uf*"

./src/analyze.py -R $report --results $path/$mocde $path/moead $path/paes $path/nsga2 --functions $functions -hl $mocde
