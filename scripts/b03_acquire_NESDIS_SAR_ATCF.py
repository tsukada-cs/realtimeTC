#%%
import os
import argparse

import pandas as pd

import Realtime


IDs = None
#%%
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--id", type=str, nargs="*", help="Target IDs in bbnnyyyy format")
args = parser.parse_args()
IDs = args.id
#%%
if IDs is None:
    IDs = pd.read_csv(f'{os.environ["HOME"]}/git/realtimeTC/data/pickup_IDs.csv')["ID"]


for target_ID in IDs:
    print(f"-- b03 (target={target_ID})")
    tcdir = f'{os.environ["HOME"]}/git/realtimeTC/data/TCs/{target_ID[-4:]}/{target_ID}'
    os.makedirs(tcdir, exist_ok=True)
    sar_NESDIS = Realtime.download_SAR_ATCF_from_NESDIS(target_ID, odir=tcdir)