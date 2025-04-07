#!/bin/bash

tmax=500.0
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
nbStates=10

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

# Loop over chi from 0.11 to 0.33 in steps of 0.01
for chi in $(seq 0.06 0.01 0.3); do
    a=$(echo "scale=5; 1 / $chi" | bc)
    echo "chi = $chi, a = $a"
    
    ./tevol_source_diff_dynnn $mu $nu_n $nu_p $K $ktau $a $kc $x0c $bl $r $nbStates $nbStates 4 1 $tmax > test.csv

    # Ensure unique file naming and fix variable expansion
    awk -F, '!seen[$1]++' test.csv > tmp.csv
    mv tmp.csv test_dir/test_${chi}_${kc}_${x0c}.csv
done
