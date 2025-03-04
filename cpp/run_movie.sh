#!/bin/bash

for ic in 4;
do
    echo doing $ic
    #                    μ   νn   νp   α    β   k   x0   K  10 11 12 TEMP LOG tmax
    ./tevol_source_diff 0.1 0.01 0.01 0.01 0.05 15.0 0.05 40 40 40 $ic 1 0 100000.0 > test.csv
    python movie.py 
    mv movie2.gif movie2_ic$ic.gif
done