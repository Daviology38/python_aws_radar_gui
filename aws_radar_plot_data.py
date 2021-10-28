import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import pyart
import tempfile
import gc
import metpy.plots as mpplots
import xarray as xr
from metpy.io import Level2File


def plot_data(datasets, station):

    locs = pyart.io.nexrad_common.NEXRAD_LOCATIONS

    f = Level2File(datasets)
    sweep = 0
    # First item in ray is header, which has azimuth angle
    az = np.array([ray[0].az_angle for ray in f.sweeps[sweep]])

    ref = f.sweeps[sweep][0][4][b'REF'][0]
    ref_range = np.arange(ref.num_gates) * ref.gate_width + ref.first_gate
    ref = np.array([ray[4][b'REF'][1] for ray in f.sweeps[sweep]])

    lat = locs[station]["lat"]
    lon = locs[station]["lon"]

    # Convert az,range to x,y
    xlocs = ref_range * np.sin(np.deg2rad(az[:, np.newaxis])) * 1000
    ylocs = ref_range * np.cos(np.deg2rad(az[:, np.newaxis])) * 1000


    #cx, cy, cz = pyart.core.antenna_to_cartesian(rng / 1000, data.variables["azimuthR"].values[0, :][:, None], data.variables["elevationR"].values[0, :][:, None])
    lla = pyart.core.cartesian_to_geographic_aeqd(xlocs, ylocs, lon, lat, R=6370997.0)

    return (
        lla,
        ref,
        f.dt.strftime("%m-%d-%Y %H:%M UTC"),
        lon,
        lat
    )
