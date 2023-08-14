#%%
import os
import argparse

import pandas as pd

import Realtime


#%%
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--id", type=str, nargs="*", help="Target IDs in bbnnyyyy format")
args = parser.parse_args()

#%%
if args.id is None:
    args.id = pd.read_csv(f'{os.environ["HOME"]}/git/realtimeTC/refdata/TCs/latest_IDlist.csv')["ID"]

odir = f'{os.environ["HOME"]}/git/realtimeTC/refdata/TCs/NESDIS_SAR_ATCF'

for target_ID in args.id:
    print(f"-- b03 (target={target_ID})")
    sar_NESDIS = Realtime.download_SAR_ATCF_from_NESDIS(target_ID, odir=odir)