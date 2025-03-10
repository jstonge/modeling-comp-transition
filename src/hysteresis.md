# Hysteresis in ecology


In ecology, alternative stable states are important because they can lead to drastic changes in the ecosystem even with small perturbations, which cannot be undone easily. 

The classical example is that of turbidity in shallow lakes, in response to excess level of nutrients (like phosphate). Something like

```tex
\dot{X} = \frac{a + X^2}{1+X^2} - rX
```

where _X_ is the ecosystem state (turbidity of the lake), while _r_ is the parameter condition (like nutrients). As you add more nutrients, nothing might happen for a while to the state of the lake. But as you hit a critical threshold, you bifurcate to a new fixed point of turbidity that is much higher than the previous one ('catastrophe' event). Unfortunately, as the story goes, to get get back to your favored equilibrium you need to remove much more nutrients from the lake than what has been allowed before. It might look like 

![](./figs/hysteresis.png)

Try explaining that to farmers than the previous allowed level of nutrients is too much now.

This example has a a single parameter _r_. In the next example popularized by Strogatz, we have the outbreak of spruce budworms in forest, which the nondimensional version looks like

```tex
\dot{X} = rX(1 - \frac{X}{K}) - \frac{X^2}{1+X^2}
```

Here, the removal of the spruce budworms _X_ is a nonlinear term, wheras the growth rate takes a logistic form with growth rate _r_ and a carrying capacity _K_. For specific value of _K_ and _r_, we might have something like

![](./figs/budworms1.png)

Then, with some algebra, Strogatz show that we have hysteresis in this 2d systems 

![](./figs/budworms2.png)

To see how the pair of parameters _r_ and _k_ impact the ecosystem, you now need a 3d plot (plot borrowed from Garfinkel et al. 2021):

![](./figs/budworms3.png)

The management story here is that if you want to get from outbreak to refugee only, you could either drastically reduce _r_ (good luck with that) or perhaps reduce a little bit _k_ and _r_ (get into the bistable region, black star), then reduce _X_ (by spraying insecticides; white star). With this strategy, the system could go back by itself in the low-X equilibrium state (red star).

In both cases, we have a single state variable driven by one or more condition parameters. In the first case, the import of nutrients is nonlinear, with the removal being linear. In the second case, we end up with the removal being nonlinear (and not dependent on any parameter), while the reproduction rate is linear. 

In ecology, there are two ways by which alternative stable states are thought to happen; either by a shift in parameters shift, or in state variables.

![](./figs/beisner2003.jpg)

The key differences are part of cultural differences in ecology:

- `community perspective`: shift in state variables (pushing a ball over a hill; landscape is broadly constant), e.g.
  - alternative interior states (predator removal or additions, Overharvesting a fishery)
  - boundary states where one or more species is absent (interspecific competition is stronger than intraspecific competition, one population will outcompete the other, Dispersal and colonization)
- `ecosystem perspective`: shift in parameters (changing the underlying landscape)


As mentionned by Giulio, we should also note that all previous examples have fixed points that are solutions of a third order equation:

```tex
ax^3+bx^2+cx+d=0
```

And the thing, as he say, is that you cannot get hysteresis with an equation of a lower order.
