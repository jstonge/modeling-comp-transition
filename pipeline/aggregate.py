import glob
import pandas as pd

all_files = glob.glob("results_*.parquet")
df_list = [pd.read_parquet(f) for f in all_files]
df_all = pd.concat(df_list, ignore_index=True)

# Now df_all has columns: id, alpha, beta, frac_prog, cost_deaths
df_all.to_parquet("all_results.parquet", index=False)
