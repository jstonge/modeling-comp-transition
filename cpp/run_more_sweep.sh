#!/bin/bash
tmax=10.0
mu=100.0
nu_n=10.0
nu_p=10.0
# ktau=15.0
# a=3.0
bl=0.1
kc=15.0
x0c=0.3
K=20
ic=4


for ktau in $(seq 5 5 20); do
    for a in $(seq 1 1 15); do
        echo $k
        ./tevol_source_diff_fancy $mu $nu_n $nu_p  $ktau $a  $bl  $kc  $x0c $K 20  20 $ic  1 $tmax > test.csv

        # Append the resulting first column along with your parameter string to test.csv
        # echo "100.0,10.0,10.0,10.0,$beta,$k,$x0,40,40,40,4,1,0,$tmax" >> test.csv

        # Ensure unique file naming and fix variable expansion
        awk -F, '!seen[$1]++' test.csv > tmp.csv
        mv tmp.csv test_dir/test_${ktau}_${a}_${kc}_${x0c}.csv
    done
done