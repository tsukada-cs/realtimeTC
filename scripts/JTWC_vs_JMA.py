# %%
import os, glob

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

import TCtools
import TCtools.dvorak

%load_ext autoreload
%autoreload 2

year = 2023
name = "KHANUN"
JTWC_key = "WP06" + str(year)
JMA_num = 6
st = pd.to_datetime("20230725T00")
et = pd.to_datetime("20230808T12")
anal_start = pd.to_datetime("20230718T23")
anal_end = pd.to_datetime("20230727T00")
Landfall_time = pd.Timestamp("2023-07-20 02")

ylim = (0,68)
ylimr = (920,1020)
category_text=["TD", "TS","Cat-1", "Cat-2", "Cat-3", "Cat-4"]

# SAR Vmax
NESDIS_Vmax_time = None #pd.to_datetime(["2023-07-23 09:43", "2023-07-24 09:52", "2023-07-25 10:00", "2023-07-25 21:55", "2023-07-26 10:09:07", "2023-07-26 22:01:56", "2023-07-26 22:02:51", "2023-07-27 10:17:38"])
NESDIS_SAR_Vmax = None #TCtools.knot_to_ms(np.array([73.74,94.61, 108.58, 98.31, 71.71, 71.30, 73.41, 87.72]))

CYCLOBS_Vmax_time = None
CYCLOBS_SAR_Vmax = None

#%%
# TCtools.renew_ibtracs()
# ibt = TCtools.get_ibt("/Users/tsukada/git/TCtools/data/IBTrACS.since1980.v04r00.nc", year=2023, name=name, storm_from=3788)
# ibt = ibt.isel(date_time=ibt["iflag"].str[0]=="O".encode())
# ibt["usa_wind"] = TCtools.knot_to_ms(ibt["usa_wind"])
ibt = TCtools.get_jtwc_bt_from_navy(JTWC_key)
ibt["usa_wind"], ibt["usa_pres"] = ibt["vmax"], ibt["pres"]

jtwc = ibt[["time","usa_wind","usa_pres"]]
jtwc["vmax_ms"] = jtwc["usa_wind"]
jtwc["pres"] = jtwc["usa_pres"]

jma = TCtools.get_jma_bt_from_DigitalTyphoon(year, JMA_num)
jma["vmax_ms"] = TCtools.knot_to_ms(jma["vmax_kt"])
jma["vmax_ms"] = jma["vmax_ms"].where(jma["vmax_ms"]>0)
jma["vmax_ms_1min"] = TCtools.knot_to_ms(TCtools.dvorak.wind10min_to_1min(jma["vmax_kt"]))


jtwc = ibt[["time","usa_wind","usa_pres"]]
jtwc["vmax_ms"] = jtwc["usa_wind"]
jtwc["pres"] = jtwc["usa_pres"]

# # best track
# jma = pd.read_csv("/Users/tsukada/git/2020_HAISHEN/data/jmaliminary.csv", parse_dates=["time"], skipinitialspace=True)
# jma["vmax_ms_1min"] = TCtools.knot_to_ms(TCtools.dvorak.wind10min_to_1min(jma["vmax"]))
# jma["vmax_ms"] = TCtools.knot_to_ms(jma["vmax"])
# jma_final = pd.read_csv("/Users/tsukada/git/2020_HAISHEN/data/JMA_final.csv", parse_dates=["time"], skipinitialspace=True)
# jma_final["vmax"] = np.where(jma_final["vmax"] > 0, jma_final["vmax"], np.nan)
# jma_final["vmax_ms_1min"] = TCtools.knot_to_ms(TCtools.dvorak.wind10min_to_1min(jma_final["vmax"]))
# jma_final["vmax_ms"] = TCtools.knot_to_ms(jma_final["vmax"])
# jtwc = pd.read_csv("/Users/tsukada/git/2020_HAISHEN/data/JTWC_preliminary.csv", parse_dates=["time"], skipinitialspace=True)
# jtwc["vmax_ms"] = TCtools.knot_to_ms(jtwc["vmax"])


# plotter
plotter = TCtools.Plotter()
year = int(jma.time.dt.year[jma.time.size//2])
month_b = jma.time.dt.strftime("%b")[jma.time.size//2]
units = "m/s"
#%% ax2_with_TPARCII final
fig, ax2 = plt.subplots(figsize=(6,4), facecolor="w")
xlim = [st,et]
category_kwargs = dict(
    category_text=category_text, windunits=units
)
ax2, ax2r = plotter.bt_intensity(ax2, jtwc["time"], jtwc["vmax_ms"], jtwc["pres"], xlim=xlim, ylim=ylim, ylimr=ylimr, windcolor="#aa6633", prescolor="#0099aa", category_kwargs=category_kwargs)
ax2, ax2r = plotter.bt_intensity(ax2, jma["time"], jma["vmax_ms_1min"], jma["pres"], xlim=xlim, ylim=ylim, ylimr=ylimr, axr=ax2r, windcolor="#aa3333", prescolor="#0066aa", plot_category=False)

ax2.plot(jma["time"], jma["vmax_ms"], ls="--", c="#aa3333", zorder=29)

ax2.set(xlabel=f"Time ({year})", ylabel=f"Maximum sustained wind ({units})")
ax2r.set_ylabel("Central pressure (hPa)", labelpad=8, rotation=-90)
ax2r.set(yticks=np.r_[ylimr[0]:ylimr[-1]+.1:10], axisbelow=True)
ax2.set_title(f'(b) Best track intensity | {name} ({year})', loc="left")
# ax2.axvspan(pd.to_datetime("2020-09-16 04"), pd.to_datetime("2020-09-16 06"), color="dimgray", ec="w", alpha=0.9, zorder=2,) #fce081
# ax2.axvspan(pd.to_datetime("2020-09-17 00"), pd.to_datetime("2020-09-17 02"), color="dimgray", ec="w", alpha=0.9, zorder=2,) #fce081

# observation
ax3 = ax2.twinx()
if CYCLOBS_Vmax_time is not None:
    ax3.scatter(CYCLOBS_Vmax_time, CYCLOBS_SAR_Vmax, marker="p", c="darkviolet", s=70, ec="k", zorder=30)
if NESDIS_Vmax_time is not None:
    ax3.scatter(NESDIS_Vmax_time, NESDIS_SAR_Vmax, marker="p", c="darkorange", s=70, ec="k", zorder=30)
ax3.axis("off")
ax3.set(ylim=ax2.get_ylim())

# Landfall
if st < Landfall_time and Landfall_time < et:
    ax2.axvline(Landfall_time, c="dimgray", ls="--", dashes=[16,4], lw=1)
    ax2.text(Landfall_time, 71, "(Landfall)", ha="center", va="bottom", c="#222222", path_effects=plotter.stroke("w",4))

ax2r.plot([], [], "o-", lw=4, c="#aa3333", mec="w", ms=4, mew=1, label="JMA Vmax (1 min via CI#)")
ax2r.plot([], [], ls="--", c="#aa3333", label="JMA Vmax (10 min)")
ax2r.plot([], [], "o-", lw=4, c="#0066aa", mec="w", ms=4, mew=1, label="JMA Pmin")
ax2r.plot([], [], "o-", lw=4, c="#aa6633", mec="w", ms=4, mew=1, label="JTWC Vmax")
ax2r.plot([], [], "o-", lw=4, c="#0099aa", mec="w", ms=4, mew=1, label="JTWC Pmin")

if CYCLOBS_Vmax_time is not None:
    ax2r.scatter([], [], marker="p", c="darkviolet", s=70, ec="k", label="SAR Vmax (CyclObs)")
if NESDIS_Vmax_time is not None:
    ax2r.scatter([], [], marker="p", c="darkorange", s=70, ec="k", label="SAR Vmax (NESDIS)")

# ax2r.axvspan([0], [1], fc="indigo", ec="w", hatch="//", alpha=0.4, label="Analysis period")

ax2r.legend(loc="upper center", bbox_to_anchor=[0.5,-0.2], fontsize=10, ncol=3, columnspacing=1, handlelength=1.2, borderpad=0.6)

fig.savefig(f"../outputs/04_{name}_intensity_pre.pdf", bbox_inches="tight", pad_inches=.1, dpi=300)

# %%
lonlim = [112,140] # longitude
latlim = [9,33] # latitude

times = pd.to_datetime(jma.time)
lons, lats = jma["lon"], jma["lat"]

# plot
fig = plt.figure(figsize=(6,6), facecolor="w")
ax1 = fig.add_subplot(111, projection=plotter.platecarree)

# ax1
ax1 = plotter.track(
    ax1, lons, lats, jma["vmax_ms_1min"], lonlim, latlim, mec="#222222", 
    ocean_color="#abc4de", dx=5, dy=4, legend_loc="lower left", 
    legend_category=["TD", "TS", "Cat-1", "Cat-2", "Cat-3", "Cat-4", "Cat-5"])
for time, lon, lat in zip(times, lons, lats):
    if time.hour != 0:
        continue
    if lon<=lonlim[0] or lonlim[1]<=lon or lat<=latlim[0] or latlim[1]<=lat:
        continue
    if time == pd.Timestamp("2020-09-10 00"):
        x = lon - 2.5
        y = lat + 1.5
    else:
        x = lon + 1.5
        y = lat + 1.5
    ax1.annotate(
        time.strftime("%d-%b"), c="#111111", fontsize=13, xy=(lon, lat), ha="center", va="center", xycoords='data', xytext=(x, y), textcoords='data',
        path_effects=plotter.stroke("w", 1.5), arrowprops=dict(arrowstyle="-", color="w", path_effects=plotter.stroke("#222222", 3)))
ax1.set_title(f"(a) Best track position (JMA) | {name} ({year})", loc="left")
fig.savefig(f"../outputs/04_{name}_position.pdf", bbox_inches="tight", pad_inches=.1, dpi=300)
# %%
