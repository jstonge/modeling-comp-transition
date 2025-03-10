#!/bin/bash

# Loop through each line of temp.csv (assumes there are 15 comma-separated fields per line)
while IFS=, read -r p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 p14 p15; do
    # Run simulation using the first 13 parameters and then the 15th as the final parameter
    # p5 is the beta value, which we use to name the output file
    echo "$p1" "$p2" "$p3" "$p4" "$p5" "$p6" "$p7" "$p8" "$p9" "$p10" "$p11" "$p12" "$p13" "$p15"
    ./tevol_source_diff "$p1" "$p2" "$p3" "$p4" "$p5" "$p6" "$p7" "$p8" "$p9" "$p10" "$p11" "$p12" "$p13" "$p15" > test.csv
     awk -F, '!seen[$1]++' test.csv > tmp.csv && mv tmp.csv test_$p5.csv
done < temp.csv

