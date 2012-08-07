# /bin/bash

path=../mocde/results/history/$1

./src/analyze.py --presentation -R presentation-$1 --results $path/mocde $path/moead $path/paes $path/nsga2 --functions "*" -hl mocde
