# Modeling Comp Transition

We first provide an overview of hysteresis in ecology, then we explain our group-based master equation model.

## Hysteresis in ecology

In ecology, alternative stable states are important because they can lead to drastic changes in the ecosystem even with small perturbations, which cannot be undone easily. 

The classical example is that of turbidity in shallow lakes, in response to excess level of nutrients (like phosphate). Something like

```tex
\dot{X} = \frac{a + X^2}{1+X^2} - rX
```

where _X_ is the ecosystem state (turbidity of the lake), while _r_ is the parameter conditions (like nutrients). As you add more nutrients, nothing might happen for a while to water clarity. But as you hit a threshold, then you bifurcate to a new fixed point of turbidity that is much higher than the previous one. Unfortunately, as the story goes, in the case of saddle-node bifurcation, you get back to the previous equilibrium state you need to remove much more nutrients from the lake than what has been allowed before. It might look like 

![](./hysteresis.png)

Try explaining that to farmers than the previous allowed level of nutrients is too much now.

Now, this example is a case in one dimension, with a single parameter _r_. In the next case popularized by Strogatz, we have the outbreak of spruce budworms in forest, which the nondimensional version looks like

```tex
\dot{X} = rX(1 - \frac{X}{K}) - \frac{X^2}{1+X^2}
```

Here, the removal of the spruce budworms _X_ is a nonlinear term, wheras the growth rate takes a logistic form with growth rate _r_ and a carrying capacity _K_. For specific value of _K_ and _r_, we might have something like

![](./budworms1.png)

Then, with some algebra, Strogatz show that we have hysteresis in this 2d systems 

![](./budworms2.png)

To see how the pair of parameters _r_ and _k_ impact the ecosystem, you now need a 3d plot (plot borrowed from Garfinkel et al. 2021):

![](./budworms3.png)

The management story here is that if you want to get from outbreak to refugee only, you could either drastically reduce _r_ (good luck with that) or perhaps reduce a little bit _k_ and _r_ (get into the bistable region, black star), then reduce _X_ (by spraying insecticides; white star). With this strategy, the system could go back by itself in the low-X equilibrium state (red star).

In both cases, we have a single state variable driven by one or more condition parameters. In the first case, the import of nutrients is nonlinear, with the removal being linear. In the second case, we end up with the removal being nonlinear (and not dependent on any parameter), while the reproduction rate is linear.

In ecology, there are two ways by which alternative stable states are thought to happen; either by a shift in parameters shift, or in state variables.

![](./beisner2003.jpg)

The key differences are part of cultural differences in ecology:

- `community perspective`: shift in state variables (pushing a ball over a hill; landscape is broadly constant), e.g.
  - alternative interior states (predator removal or additions, Overharvesting a fishery)
  - boundary states where one or more species is absent (interspecific competition is stronger than intraspecific competition, one population will outcompete the other, Dispersal and colonization)
- `ecosystem perspective`: shift in parameters (changing the underlying landscape)


## GMEs hysteresis

We are interested in modeling the varying cost-benefit ratio of having programmers in research groups. Let ${tex`G_{n,p}`} be the fraction of groups with _n_ non-programmers and _p_ programmers. We have the following model:

```tex
\begin{align*}
	\frac{d}{dt}G_{n,p} &= \mu G_{n+1,p} \cdot (n+p+1)(1-\frac{1+n+p}{k}) \\
                        &- \mu G_{n-1,p} \cdot (n+p+1)(1-\frac{1+n+p}{k}) \\
                        &+ \nu_n \Big((n+1)G_{n+1,p}-nG_{n,p}\Big) \\
	                    &+ \nu_p\Big((p+1)G_{n,p+1} - pG_{n,p} \Big) \\
						&+ \Big[ \tau_g(n+1,p-1)(1-c(n+1, p-1)G_{n+1,p-1} - \tau_g(n,p)G_{n,p} \Big] \\
	                    &+ \tau_g(n+1,p)(1-c(n+1,p))G_{n+1,p}
\end{align*}
```

where ${tex`\nu n`} and ${tex`\nu p`} are graduation rates of non-programmers and non-programmers. There is constant inflow of non-programmers in the system.

```tex
\begin{align*}
\log\Big[\tau_g(n,p; \alpha, \beta))\Big] &= \alpha (n-1) +\beta (c * p + (1-c)(p+1)) - \alpha * n + \beta * p \\
                                  &= -\alpha + \beta(1-c)
\end{align*}
```

##  Lab notes

We keep track of the different formulations of the cost functions below, from most recent to older entries

### 2024-10-03

Currently, our cost function is defined as

```tex
c(n,p) = \frac{1}{1 + e^{k \cdot ( p/n - x_0)}}
```

we typically use the following values:

```js
function c(x,k,x0) {
    return 1 / (1 + Math.exp(k*( x - x0)))
}
```

```js
Plot.plot({
    nice: true,
    grid: true,
    caption: "k=40, x0=0.25",
    x: {label:"p/n"},
    marks: [
        Plot.line(
            d3.range(0, 1, 0.01),
            { x: x => x, y: x => c(x, 40, 0.25) }
        )
    ]
})
```

with a fraction of p/n = 0, we are assuming it is impossible for non-programmers to convert into programmers. This is a bit intense. When the ratio is 0.25, we see the sharpest decline in cost (something like 1 programmer in a group of 4). This is pretty arbitrary. But the goal for now is to get some hysteresis, and we wanted a sharp decline. Finally, this sharp decline means that 40% of programmers in your team (regardless of size) is enough for anybody to successfully learn programming.


## More ideas

- For us, one idea would be that the landscape (institutions) are broadly constant, while one population (of programmers) could end up either displacing the other or could live in a bistable regime.