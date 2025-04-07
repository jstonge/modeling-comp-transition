#!/bin/bash

# Default values
tmax=200.0
mu=0.9
nu_n=0.2
nu_p=0.2
ktau=25.0
a=7.0
kc=30.0
x0c=0.4
bl=0.1
r=5.0
K=14
ic=4
nbStates=14

# Parse named arguments
for arg in "$@"
do
    case $arg in
        mu=*)     mu="${arg#*=}" ;;
        nu_n=*)   nu_n="${arg#*=}" ;;
        nu_p=*)   nu_p="${arg#*=}" ;;
        K=*)      K="${arg#*=}" ;;
        ktau=*)   ktau="${arg#*=}" ;;
        a=*)      a="${arg#*=}" ;;
        kc=*)     kc="${arg#*=}" ;;
        x0c=*)    x0c="${arg#*=}" ;;
        bl=*)     bl="${arg#*=}" ;;
        r=*)      r="${arg#*=}" ;;
        ic=*)     ic="${arg#*=}" ;;
        tmax=*)   tmax="${arg#*=}" ;;
        nbStates=*)   nbStates="${arg#*=}" ;;
        *)        echo "Unknown argument: $arg" ;;
    esac
done

# Run the loop
for ic_val in $ic;
do
    echo "$mu $nu_n $nu_p $K $ktau $a $kc $x0c $bl $r $nbStates $nbStates $ic_val 1 $tmax"
    #                           mu nu_n  nu_p ktau a  bl   kc   x0c  K 20 20 ic 1 tmax
    # ./tevol_source_diff_fancy 10.0 5.0 5.0  1.0 1.0 0.05 3.0 0.0 20 20 20 4 1 10.0 > test.csv
    ./tevol_source_diff_dynnn $mu $nu_n $nu_p $K $ktau $a $kc $x0c $bl $r $nbStates $nbStates $ic_val 1 $tmax > test.csv
    echo "plotting"
    python simple-plotting.py
done

# python movie.py 
# mv     movie2.gif movie2_ic${ic_val}.gif
