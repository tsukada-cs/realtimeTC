# %%
import argparse

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
parser.add_argument("-t", "--time_cutoff", type=float, default=24, help="Cut-off point in time for considering data as the latest (in `time_units). Data up to this hours before this cut-off point is considered as the latest data.")
parser.add_argument("-u", "--time_units", type=str, default="hour")
parser.add_argument("-o", "--opath", type=str, default="./latest_IDlist.txt", help="ID list")

args = parser.parse_args()
path_to_tclist = args.path_to_tclist
time_cutoff = args.time_cutoff
time_units = args.time_units
opath = args.opath

# %%
tclist = pd.read_csv(path_to_tclist)
lastmods = pd.to_datetime(tclist["lastmod"], format="%d-%b-%Y %H:%M")

elapsed_times = (pd.Timestamp.now("UTC").replace(tzinfo=None)-pd.Timedelta(7,"h")) - lastmods
is_latest = elapsed_times <= pd.Timedelta(time_cutoff, time_units)
# %%
latest_IDs = tclist["ID"].where(is_latest).dropna()
latest_IDs.to_csv(opath, sep="\n", index=False, header=True)
