#!/bin/bash

for ic in 0 1 3;
do
    echo doing $ic
    #                   mu, nu_n nu_p a    beta b   c0 K max1/2 IC TEMPORAL
    ./tevol_source_diff 0.1 0.01 0.03 0.01 0.04 0.5 10.0 0.5 40 40 40 $ic 1  > test.csv
    python movie.py 
    mv movie2.gif movie2_ic$ic.gif
done