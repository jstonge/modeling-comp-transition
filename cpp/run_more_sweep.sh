#!/bin/bash
x0=0.05
tmax=100.0
beta=40

for k in $(seq 1 0.5 15); do
    echo $k
    ./tevol_source_diff 100.0 10.0 10.0 10.0 $beta $k $x0 40 40 40 4 1 0 $tmax > test.csv

    # Append the resulting first column along with your parameter string to test.csv
    # echo "100.0,10.0,10.0,10.0,$beta,$k,$x0,40,40,40,4,1,0,$tmax" >> test.csv

    # Ensure unique file naming and fix variable expansion
    awk -F, '!seen[$1]++' test.csv > tmp.csv
    mv tmp.csv test_${beta}_${k}_${x0}.csv
done
