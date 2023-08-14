# %%
import os
import argparse
import datetime

import pandas as pd

import Realtime


# # [for test]
# %load_ext autoreload
# %autoreload 2
# year = 2023
# bb = "al"
# path_to_tclist = "/Users/tsukada/git/realtimeTC/refdata/TCs/tclist.csv"
# odir = "/Users/tsukada/git/realtimeTC/refdata/TCs/JTWC_pre_btk"
# no_replace = False
# force = True
# time_cutoff = 72
# time_units = "hour"
#%%
parser = argparse.ArgumentParser(description="Process year and basin arguments.")
parser.add_argument("-y", "--year", type=int, help="The year to retrieve the TC directories.")
parser.add_argument("-b", "--basins", type=str, nargs="*", choices=["AL", "EP", "WP", "IO", "SH", "al", "ep", "wp", "io", "sh"], help="The basin to retrieve the TC directories. Valid values are 'AL', 'EP', 'WP', 'IO', 'SH'.")
parser.add_argument("-p", "--path_to_tclist", type=str, default="/Users/tsukada/git/realtimeTC/refdata/TCs/tclist.csv")
parser.add_argument("-o", "--odir", type=str, default="/Users/tsukada/git/realtimeTC/refdata/TCs")
parser.add_argument("-n", "--no_replace", action="store_true")
parser.add_argument("-f", "--force", action="store_true", help="If specified, update all TCs")
parser.add_argument("-t", "--time_cutoff", type=float, default=72, help="Cut-off point in time for considering data as the potantially updated case (in `time_units). Data up to this hours before this cut-off point is considered as the latest data.")
parser.add_argument("-u", "--time_units", type=str, default="hour")

args = parser.parse_args()
year = args.year
bbs = args.basins
path_to_tclist = args.path_to_tclist
odir = args.odir
no_replace = args.no_replace
force = args.force
time_cutoff = args.time_cutoff
time_units = args.time_units

#%%
def download_and_read_btk(ID, odir):
    ds = Realtime.download_jtwc_bt_from_navy(ID, opath=f"{odir}/{ID}.txt", asxarray=True)
    return ds

def create_TC(tclist, ID, odir):
    return update_TC(tclist, ID, odir)

def update_TC(tclist, ID, odir):
    btk = download_and_read_btk(ID, odir)
    lastmod = Realtime.get_lastmod(ID)
    if ID in tclist.index: # update
        tclist.at[ID,"name"] = btk.name.item()
        tclist.at[ID,"lastmod"] = lastmod
    else: # create
        df1line = pd.DataFrame([[btk.name.item(),lastmod]], index=[ID], columns=["name","lastmod"])
        tclist = pd.concat([tclist,df1line])
    tclist = tclist.sort_index()
    return tclist
#%% main
tclist = pd.read_csv(path_to_tclist, index_col="ID", skipinitialspace=True)
lastmods = pd.to_datetime(tclist["lastmod"], format="%d-%b-%Y %H:%M")
tclist["elapsed_times"] = (pd.Timestamp.now("UTC").replace(tzinfo=None)-pd.Timedelta(hours=7)) - lastmods


for bb in bbs:
    print(f"-- {bb}")
    IDs = Realtime.get_jtwc_IDs(year, bb)
    for ID in IDs:
        if ID not in tclist.index or force:
            tclist = create_TC(tclist, ID, odir)
            print(f"-- {ID} is created")
        else:
            if tclist["elapsed_times"][ID] > pd.Timedelta(time_cutoff, time_units):
                continue
            lastmod = Realtime.get_lastmod(ID)
            if lastmod != tclist["lastmod"][ID]:
                tclist = update_TC(tclist, ID, odir)
                print(f"-- {ID} is updated")
            else:
                pass # no change

if no_replace:
    current_time = datetime.datetime.now()
    opath = os.path.dirname(path_to_tclist) + current_time.strftime("/%Y-%m-%dT%H%M%S_")+ os.path.basename(path_to_tclist)
else:
    opath = path_to_tclist

tclist["name"] = tclist["name"].str.rjust(20)
tclist.sort_index().to_csv(opath, index_label="ID", encoding="utf-8")
print(f"[SUCCESS] b01")
# %%
