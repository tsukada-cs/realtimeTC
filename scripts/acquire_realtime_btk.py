#%%
import os
import argparse

import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from tropycal import realtime

# %%
realtime_obj = realtime.Realtime(jtwc=True, jtwc_source="jtwc")
realtime_obj
# %%
dir(realtime_obj)
# %%
realtime_obj.plot_summary()
# %%
storm = realtime_obj.get_storm('WP062023').to_xarray()
storm
# %%

