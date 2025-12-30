import pandas as pd

# ----- LIST YOUR CSV FILES -----
files = [
    "sample_1_hz_0.csv",
    "sample_1_hz_1.csv",
    "sample_1_hz_2.csv",
    "sample_1_hz_3.csv",
    "sample_1_hz_4.csv",
    "sample_1_hz_5.csv",
    "sample_1_hz_6.csv",
    "sample_1_hz_7.csv",
    "sample_1_hz_8.csv"
]

# ----- READ + ALIGN COLUMNS -----
dfs = [pd.read_csv(f) for f in files]

# Union of all column names across all files
all_columns = sorted(set().union(*[df.columns for df in dfs]))

# Reindex each dataframe so columns align (missing columns become NaN)
dfs = [df.reindex(columns=all_columns) for df in dfs]

# ----- CONCATENATE -----
df = pd.concat(dfs, ignore_index=True)

# ----- SORT BY YOUR TIME COLUMN -----
# Replace "epoch" with your real column name
df["unix_time"] = pd.to_numeric(df["unix_time"], errors="coerce")
df = df.sort_values("unix_time")

# ----- SAVE OUTPUT -----
df.to_csv("combined_aligned_sorted.csv", index=False)

print("Saved combined_aligned_sorted.csv")
