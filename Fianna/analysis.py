import csv
"""
How jazz styles change across Village Preservation's Jazz Map entries, 1930s–1980s.

Each row in the CSV is one map entry (a club/studio or a musician's residence),
with the decades the map tags it with and the jazz style I assigned to it.
"""

import pandas as pd
import matplotlib.pyplot as plt

# ---- Settings -------------------------------------------------------------
CSV_FILE = "Jazz_Map_1930_1980.csv"   # change this if your file has a different name
DECADES = ["1930s", "1940s", "1950s", "1960s", "1970s", "1980s"]

# Order styles roughly by when they emerged, so charts read left to right in time
STYLE_ORDER = ["traditional/Dixieland", "swing", "bebop", "cool", "hard bop",
               "free jazz/avant-garde", "loft jazz", "fusion", "mixed", "unclear"]


# ---- 1. Load the data -----------------------------------------------------
# The file was saved from Excel, so it uses Windows encoding (cp1252), not UTF-8.
# Without this, names like "Café Bohemia" come out garbled or the read fails.
df = pd.read_csv(CSV_FILE, encoding="cp1252")
df["jazz_style"] = df["jazz_style"].fillna("unclear").str.strip()

print(f"Loaded {len(df)} entries")
print(df["type"].value_counts().to_string(), "\n")


# ---- 2. One row per entry per decade --------------------------------------
# "1950s; 1960s" becomes two rows, so each entry counts in every decade it was active.
long = df.assign(decade=df["decades"].str.split(";")).explode("decade").reset_index(drop=True)
long["decade"] = long["decade"].str.strip()
long = long[long["decade"].isin(DECADES)]          # keep only 1930s–1980s


# ---- 3. Count styles per decade -------------------------------------------
counts = pd.crosstab(long["decade"], long["jazz_style"])
counts = counts.reindex(index=DECADES, fill_value=0)
counts = counts[[s for s in STYLE_ORDER if s in counts.columns]]

print("Number of entries active in each decade, by style:")
print(counts.to_string(), "\n")

# Shares (each decade adds up to 100%) — fairer, since some decades have more entries
shares = counts.div(counts.sum(axis=1), axis=0).mul(100).round(1)
print("Share of each decade's entries, by style (%):")
print(shares.to_string(), "\n")

# The most common style in each decade, ignoring "unclear" and "mixed"
known = counts.drop(columns=["unclear", "mixed"], errors="ignore")
print("Most common style per decade:")
for decade in DECADES:
    row = known.loc[decade]
    if row.sum() == 0:
        print(f"  {decade}: no entries")
    else:
        print(f"  {decade}: {row.idxmax()} ({row.max()} of {counts.loc[decade].sum()} entries)")
print()


# ---- 4. Venues only -------------------------------------------------------
# Clubs show what audiences were hearing; residences show where musicians lived.
venue_counts = pd.crosstab(long.loc[long["type"] == "Venue/Studio", "decade"],
                           long.loc[long["type"] == "Venue/Studio", "jazz_style"])
venue_counts = venue_counts.reindex(index=DECADES, fill_value=0)
venue_counts = venue_counts[[s for s in STYLE_ORDER if s in venue_counts.columns]]
print("Venues/studios only — count by decade and style:")
print(venue_counts.to_string(), "\n")


# ---- 5. When each style first and last appears ----------------------------
decade_num = long["decade"].str[:4].astype(int)
span = (long.assign(year=decade_num)
            .groupby("jazz_style")["year"].agg(first="min", last="max", entry_decades="count")
            .reindex([s for s in STYLE_ORDER if s in long["jazz_style"].unique()]))
span["first"] = span["first"].astype(str) + "s"
span["last"] = span["last"].astype(str) + "s"
print("First and last decade each style appears (1930s–1980s):")
print(span.to_string(), "\n")


# ---- 6. Charts ------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

shares.plot(kind="bar", stacked=True, ax=axes[0], colormap="tab20", width=0.8, rot=0)
axes[0].set_title("Jazz style mix by decade (all entries)")
axes[0].set_xlabel("Decade")
axes[0].set_ylabel("Share of entries active that decade (%)")
axes[0].legend().remove()

counts.plot(kind="line", marker="o", ax=axes[1], colormap="tab20")
axes[1].set_title("Number of entries by style and decade")
axes[1].set_xlabel("Decade")
axes[1].set_ylabel("Entries active that decade")
axes[1].legend(title="Jazz style", bbox_to_anchor=(1.02, 1), loc="upper left")

plt.tight_layout()
plt.savefig("jazz_styles_by_decade.png", dpi=150)
print("Saved chart: jazz_styles_by_decade.png")
plt.show()