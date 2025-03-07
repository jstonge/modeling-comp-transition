import duckdb

conn = duckdb.connect("./param_sweep.duckdb")

# Create a table to hold (alpha,beta,...) plus status or references to output
conn.execute("""
CREATE TABLE IF NOT EXISTS param_grid (
    id INTEGER,
    alpha DOUBLE,
    beta DOUBLE,
    done BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (id)
)
""")

# Insert the parameter grid
rows = []
idx = 1
import numpy as np
alpha_values = np.arange(1, 6, 0.5)  
beta_values  = np.arange(1, 6, 0.5)
for a in alpha_values:
    for b in beta_values:
        rows.append((idx, float(a), float(b), False))
        idx += 1

conn.executemany("INSERT INTO param_grid (id,alpha,beta,done) VALUES (?,?,?,?)", rows)
conn.commit()
conn.close()
