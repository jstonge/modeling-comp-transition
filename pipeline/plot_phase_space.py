import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_parquet("all_results.parquet")

# Create pivot tables: alpha on one axis, beta on the other, values = e.g. frac_prog
pivot_frac = df.pivot_table(index="beta", columns="alpha", values="frac_prog")

plt.figure(figsize=(8,6))
plt.title("Fraction of Programmers: alpha vs. beta")
c = plt.imshow(pivot_frac, origin="lower",
               extent=[df["alpha"].min(), df["alpha"].max(),
                       df["beta"].min(), df["beta"].max()],
               aspect="auto", interpolation="nearest", cmap="viridis")
plt.colorbar(c, label="Fraction of Programmers")
plt.xlabel("alpha")
plt.ylabel("beta")
