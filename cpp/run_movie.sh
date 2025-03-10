# !/bin/bash

for ic in 4;
do
    echo doing $ic
    #                    μ    νn   νp   α    β   k   x0   K 10 11 12 TEMP LOG tmax
    # ./tevol_source_diff 0.01 0.01 0.01 60.0 1.0 0.05 40 40 40 $ic 1 0 5000.0 > test.csv
    ./tevol_source_diff 100.0 10.0 10.0 10.0 46.0 3.0 0.05 40 40 40 $ic 1 0 1000.0 > test.csv
    python movie.py 
    mv movie2.gif movie2_ic$ic.gif
done
