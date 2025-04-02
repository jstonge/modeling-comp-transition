# Programmatic parameter sweeps

To sweep for parameters and plot the phase diagram, you can add a YAML of this form in `experiments/sweeps/`

```yaml
model_version: v1
output_dir: sweep_a_ktau_v1
sweep:
  a:
    start: 1.0
    stop: 15.0
    step: 1.0
  ktau:
    start: 1.0
    stop: 15.0
    step: 1.0
fixed_parameters:
  α: 0.9
  νn: 0.2
  νp: 0.2
  K: 25
  kc: 30.0
  x0c: 0.3
  bl: 0.1
  r: 5.0
tspan: [0.0, 200.0]
grid_size: 25
```

which you then call using something like

```zsh
julia run_sweep.jl experiments/sweeps/sweep_a_x0c.yaml
```
