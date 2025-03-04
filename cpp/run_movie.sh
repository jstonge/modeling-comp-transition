#!/bin/bash

for ic in 0 1 3;
do
    echo doing $ic
    #                   μ   νn   νp   α    β    k    x0   K  10 11 12  13
    ./tevol_source_diff 0.1 0.01 0.025 0.001 0.1 40.0 0.25 40 40 40 $ic 1  > test.csv
    python movie.py 
    mv movie2.gif movie2_ic$ic.gif
done