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

What about the logistic?

```
cost(n,p; k=10, x0=0.5)1 / (1 + exp(-k * (p/n - x0)))
```

With this general form of the logistic function, we can control the steepness of the decrease (k), as well as the location of the midpoint (x0). As we reduce `k`, the decrease is less steep, but the intercept also decrease:

![](logistic-k-exp)

In this example, when `k` goes from 10 to 5, the intercept is around 0.90 (making the transition easier). Similarly, playing with x0:

![](logistic-x0-exp)

We can see that increasing `x0` means that the midpoint is more to the right. When `x0=0.5`, the midpoint between 10 (as specified by `k`), and 0 is equal to 5. In our setup, this means that when in a group of 15 people you have 1:2 programmers for non-programmers, the cost of transitionning is 0.5 (a coin flip). With `x0=0.75`, you need at least 7.5 prgorammers for the same number of non-programmers to have that cost. 

Another way to say it is that when you decrease by half x0, you need half of the programmers to have the same cost. 