# %%
import argparse

import numpy as np
import pandas as pd


# # [for test]
# %load_ext autoreload
# %autoreload 2
# path_to_tclist = "/Users/tsukada/git/realtimeTC/refdata/TCs/tclist.csv"
# time_cutoff = 24
# time_units = "hour"
# opath = "/Users/tsukada/git/realtimeTC/refdata/TCs/latest_IDlist.txt"
#%%
parser = argparse.ArgumentParser(description="Process year and basin arguments.")
parser.add_argument("path_to_tclist", type=str, help="Path to tclist.csv")
parser.add_argument("-b", "--basins", type=str, nargs="*", default=["AL","EP","WP","IO","SH"], help="Basins")
parser.add_argument("-y", "--years", type=str, nargs="*", help="Years")
parser.add_argument("-t", "--time_cutoff", type=float, default=48, help="Cut-off point in time for considering data as the latest (in `time_units). Data up to this hours before this cut-off point is considered as the latest data.")
parser.add_argument("-u", "--time_units", type=str, default="hour")
parser.add_argument("-o", "--opath", type=str, default="./latest_IDlist.csv", help="ID list")

args = parser.parse_args()
path_to_tclist = args.path_to_tclist
basins = args.basins
years = args.years
time_cutoff = args.time_cutoff
time_units = args.time_units
opath = args.opath

# %%
tclist = pd.read_csv(path_to_tclist)
lastmods = pd.to_datetime(tclist["lastmod"], format="%d-%b-%Y %H:%M")

elapsed_times = (pd.Timestamp.now("UTC").replace(tzinfo=None)-pd.Timedelta(hours=7)) - lastmods
tclist["is_latest"] = elapsed_times <= pd.Timedelta(time_cutoff, time_units)

bbs = tclist["ID"].str[:2]
tclist["valid_basin"] = np.zeros(tclist["ID"].size, bool)
for basin in basins:
    tclist["valid_basin"] += bbs == basin

yyyys = tclist["ID"].str[-4:]
if years is None:
    tclist["valid_year"] = np.ones(tclist["ID"].size, bool)
else:
    tclist["valid_year"] = np.zeros(tclist["ID"].size, bool)
    for year in years:
        tclist["valid_year"] += yyyys == year
# %%
latest_IDs = tclist["ID"].where(tclist["is_latest"]*tclist["valid_basin"]*tclist["valid_year"]).dropna()
latest_IDs.to_csv(opath, sep="\n", index=False, header=True)
# print(latest_IDs)