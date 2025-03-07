# Modeling Comp Transition

Most work is in `cpp/`. At the moment, we have a couple of helper bash scripts:

- `run_movie.sh`: run `movie.py` with different initial conditions to visualize the gif where we see the probability mass moving.
- `find_final_state.sh`: run `./tevol_source_diff` for a long time to find the final state.
- `run_sweep.sh`: takes values in `temp.csv`, produced by `find_final_state.sh`, and run `./tevo_source_diff` with tmax=timestep from the last column.