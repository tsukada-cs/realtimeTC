# %%
import os
import argparse
import datetime
import subprocess

import numpy as np
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
# no_image = False
#%%
parser = argparse.ArgumentParser(description="Process year and basin arguments.")
parser.add_argument("-y", "--year", type=int, help="The year to retrieve the TC directories.")
parser.add_argument("-b", "--basin", type=str, choices=["AL", "EP", "WP", "IO", "SH", "al", "ep", "wp", "io", "sh"], help="The basin to retrieve the TC directories. Valid values are 'AL', 'EP', 'WP', 'IO', 'SH'.")
parser.add_argument("-p", "--path_to_tclist", type=str, default="/Users/tsukada/git/realtimeTC/refdata/TCs/tclist.csv")
parser.add_argument("-o", "--odir", type=str, default="/Users/tsukada/git/realtimeTC/refdata/TCs")
parser.add_argument("-n", "--no_replace", action="store_true")
parser.add_argument("-f", "--force", action="store_true", help="If specified, update all TCs")
parser.add_argument("--no_image", action="store_true")

args = parser.parse_args()
year = args.year
bb = args.basin
path_to_tclist = args.path_to_tclist
odir = args.odir
no_replace = args.no_replace
force = args.force
no_image = args.no_image
#%%
IDs = Realtime.get_jtwc_IDs(year, bb)
tclist = pd.read_csv(path_to_tclist, index_col="ID", skipinitialspace=True)

def download_and_read_btk(ID, odir):
    ds = Realtime.download_jtwc_bt_from_navy(ID, opath=f"{odir}/{ID}.txt", asxarray=True)
    return ds

def call_p01_plot_btk(ID):
    subprocess.call(['python', '/Users/tsukada/git/realtimeTC/scripts/p01_plot_btk.py', f'--bbnnyyyy={ID}', '--odir=/Users/tsukada/git/realtimeTC/outputs/JTWC_pre_intensity'])

def create_TC(tclist, ID, odir, no_image):
    return update_TC(tclist, ID, odir, no_image)

def update_TC(tclist, ID, odir, no_image):
    btk = download_and_read_btk(ID, odir)
    lastmod = Realtime.get_lastmod(ID)
    if ID in tclist.index: # update
        tclist.at[ID,"name"] = btk.name.item()
        tclist.at[ID,"lastmod"] = lastmod
    else: # create
        df1line = pd.DataFrame([[btk.name.item(),lastmod]], index=[ID], columns=["name","lastmod"])
        tclist = pd.concat([tclist,df1line])
    tclist = tclist.sort_index()
    if not no_image:
        call_p01_plot_btk(ID)
    return tclist
#%%
for ID in IDs:
    if ID not in tclist.index or force:
        tclist = create_TC(tclist, ID, odir, no_image)
        print(f"-- {ID} is created")
    else:
        lastmod = Realtime.get_lastmod(ID)
        if lastmod != tclist["lastmod"][ID]:
            tclist = update_TC(tclist, ID, odir, no_image)
            print(f"-- {ID} is updated")
        else:
            print(f"-- {ID} is not updated")

if no_replace:
    current_time = datetime.datetime.now()
    opath = os.path.dirname(path_to_tclist) + current_time.strftime("/%Y-%m-%dT%H%M%S_")+ os.path.basename(path_to_tclist)
else:
    opath = path_to_tclist
tclist["name"] = tclist["name"].str.rjust(20)
tclist.sort_index().to_csv(opath, index_label="ID", encoding="utf-8")
print(f"[SUCCESS] check: {opath}")
# %%
