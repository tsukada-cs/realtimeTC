#%%
import os
import argparse
import subprocess

import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument("--plot_NESDIS_SAR", action="store_true", help="Plot NESDIS SAR data")
parser.add_argument("--plot_JMA", action="store_true", help="Plot JMA btk data")
args = parser.parse_args()

target_IDs = pd.read_csv(f'{os.environ["HOME"]}/git/realtimeTC/refdata/TCs/latest_IDlist.csv')
odir = f'{os.environ["HOME"]}/git/realtimeTC/outputs/JTWC_pre_intensity'

#%%
for target_ID in target_IDs["ID"]:
    print(f"-- Calling p01 (target={target_ID})")
    command = ['python', f'{os.environ["HOME"]}/git/realtimeTC/scripts/p01_plot_btk.py', f'--bbnnyyyy={target_ID}', f'--odir={odir}']

    if args.plot_JMA and target_ID[:2] == "WP":
        command.append(f'--JMA_csv={os.environ["HOME"]}/git/realtimeTC/refdata/TCs/JMA_btk/{target_ID}_JMA.csv')

    if args.plot_NESDIS_SAR:
        potential_SAR_path = f'{os.environ["HOME"]}/git/realtimeTC/refdata/TCs/NESDIS_SAR_ATCF/{target_ID}_NESDIS_SAR_ATCF.csv'
        if os.path.exists(potential_SAR_path):
            command.append(f'--sar_NESDIS_csv={potential_SAR_path}')
    
    subprocess.call(command)