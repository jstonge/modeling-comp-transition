import pandas as pd
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
import sys

DAT_DIR = Path("src/")

final_res = []
for csvfile in DAT_DIR.joinpath("hysteresis_1").glob("*"):
    df = pd.read_csv(csvfile, names=["time", "d1", "d2", "y", "costDeathsCum", "avgProgs"])
    time, _, _, _, costDeathsCum, avgProgs = df.iloc[-1, :]
    _, beta, k, x0 = csvfile.stem.split('_')
    
    final_res.append((time, costDeathsCum, avgProgs, float(beta),float(k),float(x0)))        

# df = pd.DataFrame(final_res, columns=["time", "costDeathsCum", "avgProgs", "beta", "k", "x0"]).sort_values("k")

# df.to_parquet("src/hysteresis-data.parquet")

df = pd.read_parquet("src/hysteresis-data.parquet")

buf = pa.BufferOutputStream()
table = pa.Table.from_pandas(df)
pq.write_table(table, buf, compression="snappy")

# Get the buffer as a bytes object
buf_bytes = buf.getvalue().to_pybytes()

# Write the bytes to standard output
sys.stdout.buffer.write(buf_bytes)