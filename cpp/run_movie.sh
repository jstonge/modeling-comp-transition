#!/bin/bash

# Default values
tmax=10.0
mu=10.0
nu_n=5.0
nu_p=5.0
ktau=10.0
a=1.0
bl=0.05
kc=30.0
x0c=0.1
K=20
ic=4

# Parse named arguments
for arg in "$@"
do
    case $arg in
        mu=*)     mu="${arg#*=}" ;;
        nu_n=*)   nu_n="${arg#*=}" ;;
        nu_p=*)   nu_p="${arg#*=}" ;;
        ktau=*)   ktau="${arg#*=}" ;;
        a=*)      a="${arg#*=}" ;;
        bl=*)     bl="${arg#*=}" ;;
        kc=*)     kc="${arg#*=}" ;;
        x0c=*)    x0c="${arg#*=}" ;;
        K=*)      K="${arg#*=}" ;;
        ic=*)     ic="${arg#*=}" ;;
        tmax=*)   tmax="${arg#*=}" ;;
        *)        echo "Unknown argument: $arg" ;;
    esac
done

# Run the loop
for ic_val in $ic;
do
    echo "$mu $nu_n $nu_p $ktau $a $bl $kc $x0c $K 20 20 $ic_val 1 $tmax"
    #                           mu nu_n  nu_p ktau a  bl   kc   x0c  K 20 20 ic 1 tmax
    # ./tevol_source_diff_fancy 10.0 5.0 5.0  1.0 1.0 0.05 3.0 0.0 20 20 20 4 1 10.0 > test.csv
    ./tevol_source_diff_fancy $mu $nu_n $nu_p $ktau $a $bl $kc $x0c $K 20 20 $ic_val 1 $tmax > test.csv
    echo "plotting"
    python simple-plotting.py
done
# python movie.py 
# mv movie2.gif movie2_ic${ic_val}.gif
