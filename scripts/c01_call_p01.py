#%%
import os
import subprocess

import pandas as pd

target_IDs = pd.read_csv(f'{os.environ["HOME"]}/git/realtimeTC/refdata/TCs/latest_IDlist.csv')
odir = f'{os.environ["HOME"]}/git/realtimeTC/outputs/JTWC_pre_intensity'

#%%
for target_ID in target_IDs["ID"]:
    print(f"-- Calling p01 (target={target_ID})")
    subprocess.call(['python', f'{os.environ["HOME"]}/git/realtimeTC/scripts/p01_plot_btk.py', f'--bbnnyyyy={target_ID}', f'--odir={odir}'])