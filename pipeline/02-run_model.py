import duckdb
import pandas as pd
import subprocess
import numpy as np
from multiprocessing import Pool, cpu_count

def run_one_model(args):
    """Worker function called in parallel.
       args is (row_id, alpha, beta). Returns (row_id, alpha, beta, frac_prog, cost_deaths)."""
    row_id, alpha_val, beta_val = args
    
    mu, nu_n, nu_p = 0.01, 0.01, 0.01
    k, x0, K = 15.0, 0.05, 40
    max1, max2 = 40, 40
    IC, TEMP, LOG = 4, 1, 0
    tmax = 1_000.0
    
    cmd = [
        "./tevol_source_diff",
        str(mu), str(nu_n), str(nu_p),
        str(alpha_val), str(beta_val),
        str(k), str(x0), str(K),
        str(max1), str(max2),
        str(IC),
        str(TEMP),
        str(LOG),
        str(tmax)
    ]
    completed = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True)
    output = completed.stdout
    
    lines = output.strip().split('\n')
    data = np.genfromtxt(lines, delimiter=",")
    df = pd.DataFrame(data, columns=["time","d1","d2","y","costDeathsCum"])
    
    t_max = df["time"].max()
    df_final = df[df["time"] == t_max].copy()
    df_final_nonempty = df_final[(df_final["d1"]+df_final["d2"])>0]

    df_final_nonempty["frac_state"] = (df_final_nonempty["d2"] / 
                                       (df_final_nonempty["d1"]+df_final["d2"])) \
                                      * df_final_nonempty["y"]
    fraction_prog = df_final_nonempty["frac_state"].sum()
    cost_deaths = df_final["costDeathsCum"].mean()
    
    return (row_id, alpha_val, beta_val, fraction_prog, cost_deaths)
    
conn = duckdb.connect("./param_sweep.duckdb")
    
# 1) Fetch undone rows into a Python list
rows = conn.execute("""
    SELECT id, alpha, beta FROM param_grid
    WHERE done = FALSE
    ORDER BY id
""").fetchall()
conn.close()

# 2) Use a pool of workers
pool_size = cpu_count()  
with Pool(pool_size) as p:
    results = p.map(run_one_model, rows)

# 3) After parallel runs finish, store results and update DB
conn = duckdb.connect("../param_sweep.duckdb")
for (row_id, alpha_val, beta_val, frac_prog, cost_deaths) in results:
    # write parquet
    df_res = pd.DataFrame([{
        "id": row_id,
        "alpha": alpha_val,
        "beta": beta_val,
        "frac_prog": frac_prog,
        "cost_deaths": cost_deaths
    }])
    df_res.to_parquet(f"results_{row_id}.parquet")
    
    # mark as done in DB
    conn.execute("UPDATE param_grid SET done=TRUE WHERE id=?", (row_id,))

conn.commit()
conn.close()