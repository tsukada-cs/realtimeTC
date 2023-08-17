#%%
import os
import argparse

import pandas as pd

import Realtime


IDs = ["WP012022"]
#%%
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--id", type=str, nargs="*", help="Target IDs in bbnnyyyy format")
args = parser.parse_args()
IDs = args.id
#%%
tclist = pd.read_csv(f'{os.environ["HOME"]}/git/realtimeTC/data/tclist.csv', index_col="ID")

if IDs is None:
    IDs = pd.read_csv(f'{os.environ["HOME"]}/git/realtimeTC/data/pickup_IDs.csv')["ID"]

#%%
current_year = str(pd.Timestamp.now().year)
JMA_mapping = Realtime.get_JMA_number_name_mapping(current_year)

for target_ID in IDs:
    if target_ID[:2] != "WP":
        continue
    print(f"-- b04 (target={target_ID})")
    tcdir = f'{os.environ["HOME"]}/git/realtimeTC/data/TCs/{target_ID[-4:]}/{target_ID}'
    os.makedirs(tcdir, exist_ok=True)


    if target_ID[-4:] != current_year:
        JMA_mapping.update(Realtime.get_JMA_number_name_mapping(target_ID[-4:]))

    name = tclist["name"][target_ID].strip()
    
    if name not in JMA_mapping.keys():
        continue
    number = JMA_mapping[name]
    ds = Realtime.get_jma_bt_from_DigitalTyphoon(target_ID[-4:], number).drop("index")
    if ds.time.size > 0:
        ds["time"] = ds["time"].dt.strftime("%Y-%m-%d %H%M")
    oname = f'{tcdir}/{target_ID}_JMA_btk.csv'
    ds.to_pandas().to_csv(oname, index=True, index_label="time")
# %%
