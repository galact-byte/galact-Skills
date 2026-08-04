import pandas as pd
import glob, json

files = sorted(glob.glob("raw/*.parquet"))
frames = []
for f in files:
    split = f.split("/")[-1].split("-")[0]
    df = pd.read_parquet(f)
    df["__split"] = split
    frames.append(df)
    print(f"{split}: rows={len(df)}")

df = pd.concat(frames, ignore_index=True)
print("\n=== TOTAL ROWS:", len(df))
print("\n=== COLUMNS / DTYPES ===")
print(df.dtypes)

print("\n=== NULL COUNTS ===")
print(df.isnull().sum())

# id duplicates
print("\n=== id duplicates ===", df["id"].duplicated().sum())
print("unique ids:", df["id"].nunique())

# substate distribution
print("\n=== substate ===")
print(df["substate"].value_counts(dropna=False))

# visibility
print("\n=== visibility ===")
print(df["visibility"].value_counts(dropna=False))

# has_bounty
print("\n=== has_bounty? ===")
print(df["has_bounty?"].value_counts(dropna=False))

# vulnerability_information empties
vi = df["vulnerability_information"].fillna("")
print("\n=== vulnerability_information ===")
print("empty/na:", (vi.str.strip() == "").sum())
print("len<50:", (vi.str.len() < 50).sum())
print("len<20:", (vi.str.len() < 20).sum())
print("median len:", int(vi.str.len().median()))
print("max len:", int(vi.str.len().max()))

# redaction blocks (full-block char U+2588)
red = vi.str.contains("\u2588", regex=False)
print("contains redaction blocks:", red.sum())

# weakness null
print("\n=== weakness present ===")
wk = df["weakness"].apply(lambda x: x is not None and isinstance(x, dict) and x.get("name"))
print("with weakness name:", wk.sum(), "without:", (~wk.astype(bool)).sum())

# original_report_id (duplicate marker)
print("\n=== original_report_id (dup source) non-null ===")
print(df["original_report_id"].notnull().sum())

# structured_scope max_severity
def sev(x):
    if isinstance(x, dict):
        return x.get("max_severity")
    return None
print("\n=== max_severity ===")
print(df["structured_scope"].apply(sev).value_counts(dropna=False))

# sample nested reporter/team
print("\n=== sample reporter ===")
print(json.dumps(df.iloc[0]["reporter"], default=str)[:300])
print("\n=== sample team ===")
print(json.dumps(df.iloc[0]["team"], default=str)[:300])
