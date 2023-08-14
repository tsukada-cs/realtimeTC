#%%
import os
import argparse

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import TCtools
import Realtime

# [for test]
# %load_ext autoreload
# %autoreload 2
# fpath = f"{os.environ['HOME']}/git/realtimeTC/refdata/TCs/JTWC_pre_intensity/WP072023.txt"
# odir = f"{os.environ['HOME']}/git/realtimeTC/outputs/JTWC_pre_intensity"
# st = None
# et = None
# sar_NESDIS_csv = None
#%%
parser = argparse.ArgumentParser(description="Process year and basin arguments.")
parser.add_argument("--bbnnyyyy", type=str, help="The ID for target TC")
parser.add_argument("--fpath", type=str, help="The filepath for target besttrack file")
parser.add_argument("-o", "--odir", type=str, default="/Users/tsukada/git/realtimeTC/outputs/JTWC_pre_intensity")
parser.add_argument("-s", "--st", type=str, help="Start time to plot in time recognizable format")
parser.add_argument("-e", "--et", type=str, help="End time to plot in time recognizable format")
parser.add_argument("--sar_NESDIS_csv", type=str, help="path to NESDIS-SAR Vmax listing file")
args = parser.parse_args()

if args.fpath is not None and args.bbnnyyyy is not None:
    raise ValueError("fpath and bbnnyyyy must not be specified simultaneously")
elif args.fpath is None and args.bbnnyyyy is None:
    raise ValueError("fpath or bbnnyyyy is mandatory")

fpath = args.fpath
bbnnyyyy = args.bbnnyyyy.upper()
odir = args.odir
st = args.st
et = args.et
sar_NESDIS_csv = args.sar_NESDIS_csv

# %%
if fpath is not None:
    ds = Realtime.open_jtwc_bt_file(fpath)
else:
    ds = Realtime.get_jtwc_bt_from_navy(bbnnyyyy)
year = ds.year.item()
name = ds.name.item()
nnb = ds.nnb.item()
month_b = ds.time[0].dt.strftime("%b").item()
units = "m/s"

if st is None:
    st = pd.to_datetime(ds.time[0].item()) - pd.Timedelta(24, "hour")
if et is None:
    et = pd.to_datetime(ds.time[-1].item()) + pd.Timedelta(24, "hour")
#%% intensity
plotter = TCtools.Plotter()
fig, ax = plt.subplots(figsize=(8,4.5), facecolor="w")
xlim = [st,et]
ylim_vmax = [0,100]
ylim_pres = [850,1050]

max_vmax = ds["vmax"].max().round(1).item()
min_pres = ds["pres"].min().round().astype(int).item()

category_kwargs = dict(
    windunits=units,
    category_text=["TD","TS","Cat-1","Cat-2","Cat-3","Cat-4","Cat-5"],
    spancolor="#f6efe6", 
    lighttextcolor="#ffffff",
    darktextcolor="#ab6633", 
    fontsize=11,
)

ax, axr = plotter.bt_intensity(ax, ds["time"], ds["vmax"], ds["pres"], xlim=xlim, ylim=ylim_vmax, ylimr=ylim_pres, 
                            windcolor="#aa6633", prescolor="#0099aa", lw=4, stroke_lw=6, s=25, ew=0.9, 
                            category_kwargs=category_kwargs, vmax_is_front=True)
ax.grid(ls="-", c="#cccccc", axis="y", lw=0.5, zorder=1)

ax.set(xlabel=f"Time ({year})", ylabel=f"Maximum sustained wind ({units})")
ax.set(yticks=np.r_[ylim_vmax[0]:ylim_vmax[-1]-10+.1:10])
ax.set_title(f'[{nnb}] {name} ({year}) | Lifetime max intensity: {max_vmax} m/s ({min_pres} hPa)', loc="left")

axr.set(yticks=np.r_[ylim_pres[0]:ylim_pres[-1]-20+.1:20], axisbelow=True)
axr.set_ylabel("Central pressure (hPa)", labelpad=8, rotation=-90)

# ax.plot([], [], "o-", lw=4, c="#aa3333", mec="w", ms=4, mew=1, label="JMA Vmax (1 min via CI#)")
# ax.plot([], [], ls="--", c="#aa3333", label="JMA Vmax (10 min)")
# ax.plot([], [], "o-", lw=4, c="#0066aa", mec="w", ms=4, mew=1, label="JMA Pmin")
ax.plot([], [], "o-", lw=4, c="#aa6633", mec="w", ms=4.5, mew=0.8, label="JTWC Vmax")
ax.plot([], [], "o-", lw=4, c="#0099aa", mec="w", ms=4.5, mew=0.8, label="JTWC Pmin")

# observation: SAR NESDIS
if sar_NESDIS_csv is not None:
    sar_NESDIS = pd.read_csv(sar_NESDIS_csv)
    if sar_NESDIS.index.size >= 1:
        ax.scatter(sar_NESDIS["time"], sar_NESDIS["vmax"], marker="p", c="darkorange", s=70, ec="k", zorder=6, label="SAR Vmax (NESDIS)")

# sar_IFREMER = Realtime.download_SAR_ATCF_from_IFREMER(ds["bbnnyyyy"].item())
# if sar_IFREMER.index.size >= 1:
#     ax.scatter(sar_IFREMER.time, sar_IFREMER.vmax, marker="p", c="darkviolet", s=70, ec="k", zorder=6, label="SAR Vmax (IFREMER)")

# # Landfall
# if st < Landfall_time and Landfall_time < et:
#     ax.axvline(Landfall_time, c="dimgray", ls="--", dashes=[16,4], lw=1)
#     ax.text(Landfall_time, 71, "(Landfall)", ha="center", va="bottom", c="#222222", path_effects=plotter.stroke("w",4))

if ds["vmax"].max() > 90 or ds["pres"].max() > 1030:
    ax.legend(loc="upper center", bbox_to_anchor=[0.5,-0.17], fontsize=10, ncol=3, columnspacing=1, handlelength=1.2, borderpad=0.6, frameon=False)
else:
    ax.legend(loc="best", fontsize=10, ncol=3, columnspacing=1, handlelength=1.2, borderpad=0.6, frameon=False)

if fpath is not None:
    oname = os.path.basename(fpath)[:-4] + ".png"
else:
    oname = bbnnyyyy.upper() + ".png"

fig.savefig(f"{odir}/{oname}", dpi=300, bbox_inches="tight", pad_inches=.1)

# %%
