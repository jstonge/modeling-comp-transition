import re
import matplotlib.cm as cm
import matplotlib.colors as colors
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


FIG_DIR = Path("figs")
CPP_DIR = Path("cpp")

# 1) Gather all files matching "test_*.csv"
file_list = sorted(
    CPP_DIR.glob("test_*.csv"), 
    key=lambda x: int(x.stem.split('_')[1])
)

results = []  # will hold tuples of (alpha, frac_prog, cost_deaths)
for fname in file_list:
    # break
    # 2) Extract alpha from filename: e.g. "test_0.01.csv" -> alpha=0.01
    match = re.search(r"test_([0-9.]+)", fname.stem)
    if not match:
        continue
    alpha_val = float(match.group(1))

    # 3) Read the CSV
    #    We'll assume columns are: time, d1, d2, y, costDeathsCum
    #    since you used `cout << t << "," << d1 << "," << d2 << "," << y[d1][d2] << "," << costDeathsCum << "\n";`
    df = pd.read_csv(fname, names=["time","d1","d2","y","costDeathsCum","avgProgs"])

    # 4) Identify the final time
    t_max = df["time"].max()

    # 5) Subset data to only that final time
    df_final = df[df["time"] == t_max].copy()

    # 6) Compute fraction of programmers
    #    We do sum(d2/(d1+d2)*y) over all (d1, d2) where d1+d2>0
    #    ignoring states with d1+d2==0.
    df_final_nonempty = df_final[(df_final["d1"]+df_final["d2"])>0]
    df_final_nonempty["frac_state"] = (df_final_nonempty["d2"] /
                                       (df_final_nonempty["d1"]+df_final_nonempty["d2"])) \
                                      * df_final_nonempty["y"]
    fraction_prog = df_final_nonempty["frac_state"].sum()

    # 7) costDeathsCum is typically the same for all rows at final time,
    #    so we can take an average or the last row. Let's do a mean:
    cost_deaths = df_final["costDeathsCum"].mean()

    # 8) Store the result
    results.append( (alpha_val, fraction_prog, cost_deaths) )

# Convert results to a DataFrame
df_out = pd.DataFrame(results, columns=["alpha","frac_prog","cost_deaths"])
df_out.sort_values("alpha", inplace=True)  # sort by alpha

# 2) Extract columns into arrays (this is just an example; adapt to your actual headers)
alpha_vals = df_out["alpha"].values
frac_prog  = df_out["frac_prog"].values
cost_deaths = df_out["cost_deaths"].values

# 3) Create subplots
fig, ax = plt.subplots(2, 1, sharex=True, figsize=(6, 8))

# --- Top plot: fraction of programmers vs. alpha
ax[0].plot(alpha_vals, frac_prog, 'o-', color='midnightblue', label="Programmer Fraction")
ax[0].set_ylabel("Final Fraction of Programmers")
ax[0].grid(True)
ax[0].legend()

# --- Bottom plot: cost-based departures vs. alpha
ax[1].plot(alpha_vals, cost_deaths, 'o-', color='darkred', label="Cost-Based Departures")
ax[1].set_xlabel(r"$\beta$ (programmer benefit)")
ax[1].set_ylabel("Cumulative Cost-Based Departures")
ax[1].grid(True)
ax[1].legend()

plt.suptitle(r"$\alpha$ (non-progs beneftis) fixed at 10.0;k=3.0, x0=0.05")
plt.tight_layout()
# plt.savefig(FIG_DIR/"alpha_sweep.svg")
plt.show()

# -----------



file_list = sorted(
    CPP_DIR.glob("tmp_data_dir/test_*.csv"), 
    key=lambda x: int(x.stem.split('_')[1])
)

alpha_vals = []
for fname in file_list:
    match = re.search(r"test_([0-9.]+)", fname.stem)
    # if float(match.group(1)) == 4:
    #     continue
    if match:
        alpha_vals.append(float(match.group(1)))
alpha_vals = np.array(alpha_vals)

# Create normalization and choose a colormap
norm = colors.Normalize(vmin=alpha_vals.min(), vmax=alpha_vals.max())
cmap = cm.viridis  # or choose any other colormap


results = [] 

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

for fname in file_list:
    # fname = file_list[30]
    # Extract alpha from filename, e.g. "test_0.01.csv" -> alpha=0.01
    match = re.search(r"test_([0-9.]+)", fname.stem)
    if not match:
        continue
    alpha_val = float(match.group(1))
    
    color = cmap(norm(alpha_val))

    df = pd.read_csv(fname, names=["time", "d1", "d2", "y", "costDeathsCum", "avgProgs"])

    last_row = df.iloc[-1,:]

    costDeathsCum_norms = last_row.costDeathsCum / last_row.time

    plt.plot(costDeathsCum_norms, last_row.avgProgs, 'o', color=color, label=f"alpha={alpha_val}")
    
ax.set_xlabel("costDeathsCum")
ax.set_ylabel("avgProgs")
ax.grid(True)
plt.suptitle(r"")

sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, label='alpha')

plt.tight_layout(rect=[0, 0, 0.75, 1])  # Adjust layout to accommodate the external legend
plt.show()



# ----------- output to observable

file_list = sorted(
    CPP_DIR.glob("test_*.csv"), 
    key=lambda x: int(x.stem.split('_')[1])
)

results = [] 
for fname in file_list:
    df = pd.read_csv(fname, names=["time", "d1", "d2", "y", "costDeathsCum", "avgProgs"])
    match = re.search(r"test_([0-9.]+)", fname.stem)
    if not match:
        continue
    
    alpha_val = float(match.group(1))
    # color = cmap(norm(alpha_val))
    t_col = df.time.to_numpy()
    cost_cum = df.costDeathsCum.to_numpy()
    avg_progs = df.avgProgs.to_numpy()
    unique_times = np.unique(t_col)

    cost_vs_time = []
    avg_progs_time = []
    for t_val in unique_times:
        mask = (t_col == t_val)
        cost_now = np.mean(cost_cum[mask])
        avg_progs_now = np.mean(avg_progs[mask])
        cost_vs_time.append(cost_now)
        avg_progs_time.append(avg_progs_now)
    
    results.append(pd.DataFrame({"time":unique_times, "avgProgs": avg_progs_time, "cost":cost_vs_time, "alpha": alpha_val}))

all_dfs = pd.concat(results)    
all_dfs.to_csv("src/cost_vs_time_k1.csv", index=False)
