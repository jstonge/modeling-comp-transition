### Compiling

On my m1 mac:

```zsh
g++ -std=c++14 -O3 -o tevol_source_diff ./tevol_source_diff.cpp $(gsl-config --cflags) $(gsl-config --libs)
```

### Parameter sweep:

```zsh
for i in `seq 0.9 0.001 0.999`; do ./tevol_source_diff 0.1 0.01 0.03 0.01 0.47 0.5 $i 40 40 40 3 0 > test/$i.csv; done
```

See `concat.py` to concatenate and visualize result from previous sweep.

### Animation. 

First modify `run_movie.sh`, then

```
sh run_movie.sh
```

In the list of arguments, the last number is a flag saying we want the temporal output:  `0.1 0.01 0.03 0.01 0.47 0.5 40 40 40 40 $ic 1 `. For each set of arguments, we look at the different initial conditions, aka

```
0. y[0][0] = 1.0; last_avg = 0.0;
1. y[0][max2-1] = 1.0; last_avg = 1.0;
3. y[max1-1][0] = 1.0; last_avg = 0.0;
```

where `y[0][max2-1]` is maxing #programmers, while `y[max1-1][0]` is maxing number of non-programmers.

## Notes

#### Playing with $\alpha$ and $\beta$

The relative benefits of learning to code programmers is a key quantity; of course everybody wants programmers if they are 10x more productive than non-programmers.

#### Playing with different cost functions:

In (A), adding one programmer to a group makes a huge difference. In a group of 20, it decreases the cost by 20%. In (B), we reduce that number of around 7%. Moreover, as you add more and more programmers, to the point where you have 50/50, in (A) this goes to zero whereas in (B) the cost converge towards .30.

```
(A) c0*exp(-3.0*p/(1.0*n)); --> (B) c0*exp(-1.0*p/(1.0*n));
```

`results:` Programmers and large groups are overly favored. 