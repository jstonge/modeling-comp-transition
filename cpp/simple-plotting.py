import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# data = np.genfromtxt("temp.csv", delimiter=",")
# plt.plot(range(len(data)), data[:, -1], marker="o")

# 1) Load data from CSV
#    Format per line:  t, d1, d2, y[d1][d2], costDeathsCum
data = np.genfromtxt("test.csv", delimiter=",")

# 2) Extract columns into clearer names
t_col      = data[:, 0]
d1_col     = data[:, 1].astype(int)
d2_col     = data[:, 2].astype(int)
y_col      = data[:, 3]
cost_cum   = data[:, 4]  # costDeathsCum
avg_progs  = data[:, 5]  


unique_times = np.unique(t_col)

df = pd.DataFrame(data, columns=["t", "d1", "d2", "y", "cost", "avg_progs"])

# check first, second and last for prob leaks

print(df[df.t == unique_times[0]].y.sum())
assert (df[df.t == unique_times[0]].y.sum() >= 0.999) & (df[df.t == unique_times[0]].y.sum() <= 1.001)

print(df[df.t == 2].y.sum())
assert (df[df.t == 2].y.sum() >= 0.999) & (df[df.t == 2].y.sum() <= 1.001)

print(df[df.t == df.t.max()].y.sum())
assert (df[df.t == unique_times[len(unique_times)-1]].y.sum() >= 0.999) & (df[df.t == unique_times[len(unique_times)-1]].y.sum() <= 1.001)

def plot_prog_vs_nonprog_hm(i):
  # 2) Identify columns
  times = data[:, 0]
  d1s = data[:, 1].astype(int)
  d2s = data[:, 2].astype(int)
  
  t_final = unique_times[i-1]

  # 4) Filter rows for final time
  mask_final = (times == t_final)
  final_rows = data[mask_final]

  # 5) Create 'res' array sized to cover all d1,d2
  max_d1 = np.max(d1s) + 1
  max_d2 = np.max(d2s) + 1

  # Initialize res with -7 (log10 scale for 0-ish)
  res = np.full((max_d1, max_d2), -7.0)

  # 6) Fill 'res' with log10(prob)
  for row in final_rows:
      d1 = int(row[1])
      d2 = int(row[2])
      y_val = row[3]
      if y_val > 1e-6:
          res[d1, d2] = np.log10(y_val)
          # res[d1, d2] = y_val
      else:
          res[d1, d2] = np.nan  # effectively "below detection"

  # 7) Plot
  fig, ax = plt.subplots(figsize=(6, 6))

  # The vmin/vmax set the color scale range
  im = ax.imshow(res, cmap='RdYlGn', origin='lower', vmin=-6, vmax=0.0)
  # im = ax.imshow(res, cmap='RdYlGn', origin='lower', vmin=0.0, vmax=1.0)

  cbar = fig.colorbar(im, ax=ax)
  cbar.set_label("log10(prob) of groups")  # or "log10(density)"

  ax.invert_yaxis()
  ax.set_xlabel("number of programmers (d2)")
  ax.set_ylabel("number of non-programmers (d1)")
  ax.set_title(f"Final Distribution at t={t_final}")

  plt.savefig("final.svg")
  plt.show()


print(df[df.t == unique_times[10]].y.sum())
plot_prog_vs_nonprog_hm(10)
print(df[df.t == unique_times[100]].y.sum())
plot_prog_vs_nonprog_hm(100)
print(df[df.t == df.t.max()].y.sum())
plot_prog_vs_nonprog_hm(len(unique_times))

print(f"final average number of programmers: {df.iloc[-1, -1]}")

# dedup_df = df[~df.t.duplicated()]
# sns.set_style("whitegrid")

# sns.lineplot(x="t", y="cost", data=dedup_df)
# plt.ylabel("Cumulative Cost-Based Deaths")

# sns.lineplot(x="t", y="avg_progs", data=dedup_df)



# def plot_groups_wo_progs():
#   """Plot 'mass in no-programmer states' vs. time"""
#   # For each time, sum the probability (or population) in states with d2 = 0
#   no_prog_values = []  # will store sum of y where d2=0
#   for t_val in unique_times:
#       # find rows for this time
#       mask = (t_col == t_val)
#       # sum over states that have d2=0
#       sum_no_prog = np.sum(y_col[mask & (d2_col == 0)])
#       no_prog_values.append(sum_no_prog)
      
#   plt.plot(unique_times, no_prog_values)
#   plt.xlabel("Time")
#   plt.ylabel("Probability mass with no programmers (d2=0)")
#   plt.title("Fraction (or number) of Groups with No Programmers Over Time")
#   plt.show()

# def plot_groups_w_progs():
#   """Plot 'mass in no-programmer states' vs. time"""
#   # For each time, sum the probability (or population) in states with d2 = 0
#   prog_values = []  # will store sum of y where d2=0
#   for t_val in unique_times:
#       # find rows for this time
#       mask = (t_col == t_val)
#       # sum over states that have d2=0
#       sum_no_prog = np.sum(y_col[mask & (d2_col == 0)])
#       prog_values.append(sum_no_prog)
      
#   plt.plot(unique_times, prog_values)
#   plt.xlabel("Time")
#   plt.ylabel("Probability mass with programmers (d2=0)")
#   plt.title("Fraction (or number) of Groups with Programmers Over Time")
#   plt.show()

# def plot_cost_deaths_cum():
#   """Plot costDeathsCum over time"""
#   # For each time, gather the costDeathsCum values
#   #    costDeathsCum should be identical for all rows with the same t
#   #    but in case it's not, you can average or take the max.
#   cost_vs_time = []
#   for t_val in unique_times:
#       mask = (t_col == t_val)
#       # The costDeathsCum is presumably the same for all (d1, d2) at this time,
#       # so let's just take the first row's value or an average:
#       cost_now = np.mean(cost_cum[mask])  
#       cost_vs_time.append(cost_now)

#   plt.plot(unique_times, cost_vs_time)
#   plt.xlabel("Time")
#   plt.ylabel("Cumulative Cost-Based Deaths")
#   plt.title("Evolution of Cost-Based Deaths Over Time")
#   plt.show()


# # plot_groups_w_progs()
# plot_cost_deaths_cum()

# # Main quest: 
# # get out of that transient state  where >5%
# # of groups at equilibrim  without programmers 
# # in the group. One of two objectives:
# # 1) minimize the number of sacrified students during
# #    the transition towards more programmers. 
# # 2) make the transition at a faster rate. That is
# #    time before the end of the transient dynamics.