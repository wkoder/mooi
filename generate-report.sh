#! /bin/bash

path=../mocde/results/history/$1
#mocde=mocde-randbest1-1.0-0.1
mocde=mocde
FUNCTIONS="zdt* dtlz*"
#FUNCTIONS="zdt* dtlz* uf*"

./src/analyze.py -R report-$1 --results $path/$mocde $path/moead $path/paes $path/nsga2 --functions $FUNCTIONS -hl $mocde
