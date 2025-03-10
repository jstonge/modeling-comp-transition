import pandas as pd
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
import sys

# DAT_DIR = Path("src/")

# dfs = []
# for mydir in DAT_DIR.glob("*_data_dir"):
#     for csvfile in mydir.glob("test_*"):
        
#         df=pd.read_csv(csvfile, names=["time", "d1", "d2", "y", "costDeathsCum", "avgProgs"])
#         df['beta']=csvfile.stem.split('_')[1]
#         df['k']=mydir.stem.split('_')[0].split('k')[1]

#         dfs.append(df)

# df = pd.concat(dfs)



# To reduce memory usage
# scale_factor = 1000  # Convert to a large integer scale
# df['time_scaled'] = (df['time'] * scale_factor).astype(int)
# df = df[df['time_scaled'] % int(0.03 * scale_factor) == 0].drop(columns=['time_scaled']).reset_index(drop=True)

# df.to_csv("tradeoff.csv", index=False)

df = pd.read_csv("src/tradeoff.csv")

buf = pa.BufferOutputStream()
table = pa.Table.from_pandas(df)
pq.write_table(table, buf, compression="snappy")

# Get the buffer as a bytes object
buf_bytes = buf.getvalue().to_pybytes()

# Write the bytes to standard output
sys.stdout.buffer.write(buf_bytes)