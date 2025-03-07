# !/bin/bash

for x in $(seq 1 1 60); do
    ./tevol_source_diff 100.0 10.0 10.0 10.0 $x 3.0 0.05 40 40 40 4 1 0 100.0 > test.csv
    # Process test.csv, storing the first column of each unique row based on $6,
    # and print the first column of the last unique row.
    first_col_last_row="$(awk -F, '!seen[$6]++ {last=$1} END {print last}' test.csv)"
    # Append the resulting first column along with your parameter string to temp.csv
    echo "100.0,10.0,10.0,10.0,$x,3.0,0.05,40,40,40,4,1,0,100.0,$first_col_last_row" >> temp.csv
done