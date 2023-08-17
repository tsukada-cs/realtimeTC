#%%
import os
import argparse
import subprocess

import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument("--plot_NESDIS_SAR", action="store_true", help="Plot NESDIS SAR data")
parser.add_argument("--plot_JMA", action="store_true", help="Plot JMA btk data")
args = parser.parse_args()

target_IDs = pd.read_csv(f'{os.environ["HOME"]}/git/realtimeTC/data/pickup_IDs.csv')

#%%
for target_ID in target_IDs["ID"]:
    print(f"-- Calling p01 (target={target_ID})")
    tcdir = f'{os.environ["HOME"]}/git/realtimeTC/data/TCs/{target_ID[-4:]}/{target_ID}/'
    odir = f'{tcdir}/outputs'
    os.makedirs(odir, exist_ok=True)
    command = ['python', f'{os.environ["HOME"]}/git/realtimeTC/scripts/p01_plot_btk.py', f'--bbnnyyyy={target_ID}', f'--odir={odir}']

    if args.plot_JMA and target_ID[:2] == "WP":
        potential_JMA_path = f'{tcdir}/{target_ID}_JMA_btk.csv'
        if os.path.exists(potential_JMA_path):
            command.append(f'--JMA_csv={potential_JMA_path}')

    if args.plot_NESDIS_SAR:
        potential_SAR_path = f'{tcdir}/{target_ID}_NESDIS_SAR.csv'
        if os.path.exists(potential_SAR_path):
            command.append(f'--sar_NESDIS_csv={potential_SAR_path}')
    
    subprocess.call(command)