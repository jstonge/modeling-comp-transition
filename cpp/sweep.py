import glob
import re
import pandas as pd
import matplotlib.pyplot as plt

# 1) Find all files that match the pattern "test_<something>.csv"
file_list = sorted(glob.glob("test_*.csv"))

alphas = []
final_fractions = []

for filename in file_list:
    # filename = file_list[0]
    # 2) Extract the numeric part from the filename (e.g. 0.008 from "test_0.008.csv")
    match = re.search(r"test_([0-9\.]+)\.csv", filename)
    if not match:
        continue
    alpha_val = float(match.group(1))
    
    # 3) Read the CSV. Adjust depending on how your data is structured
    df = pd.read_csv(filename, header=None)  
    
    # For instance, if you're saving columns: time, mu, nu_n, ..., final_fraction
    # you might do: 
    # df = pd.read_csv(filename, names=["time", "mu", "nu_n", "nu_p", "alpha", 
    #                                   "beta", "k", "x0", "K", "IC", "fraction_prog"])

    # 4) Identify the final fraction of programmers
    #    If your file is a time series, you can take the last row's fraction.
    #    If it's just one line, you can read directly.
    # Example if the fraction is in the last column:
    final_fraction = df.iloc[-1, -1]  # last row, last column
    
    alphas.append(alpha_val)
    final_fractions.append(final_fraction)

# 5) Plot
plt.plot(alphas, final_fractions, marker='o', linestyle='--')
plt.xlabel("alpha")
plt.grid()
plt.ylabel("Final fraction of programmers")
plt.title("Bistability / Critical Transition Check")
plt.show()