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


def plot_data(datasets):

    vars_to_drop = [
        "Reflectivity_HI",
        "RadialVelocity_HI",
        "RadialVelocity",
        "RadialVelocity_HI",
        "SpectrumWidth_HI",
        "SpectrumWidth",
        "DifferentialReflectivity_HI",
        "DifferentialReflectivity",
        "CorrelationCoefficient_HI",
        "CorrelationCoefficient",
        "DifferentialPhase_HI",
        "DifferentialPhase",
    ]
    locs = pyart.io.nexrad_common.NEXRAD_LOCATIONS

    count = 0

    ref_norm, ref_cmap = mpplots.ctables.registry.get_with_steps(
        "NWSReflectivity", 5, 5
    )

    def new_map(fig, lon, lat):
        # Create projection centered on the radar. This allows us to use x
        # and y relative to the radar.
        proj = ccrs.LambertConformal(central_longitude=lon, central_latitude=lat)

        # New axes with the specified projection
        ax = fig.add_axes([0.02, 0.02, 0.96, 0.96], projection=proj)

        # Add coastlines and states
        ax.add_feature(cfeature.COASTLINE.with_scale("50m"), linewidth=2)
        ax.add_feature(cfeature.STATES.with_scale("50m"))

        return ax

    file = datasets

    data = xr.open_dataset(
        file.access_urls["OPENDAP"], decode_times=False, drop_variables=vars_to_drop
    )
    station = data.attrs["Station"]
    loc = station

    lat = locs[loc]["lat"]
    lon = locs[loc]["lon"]
    elev = locs[loc]["elev"]

    sweep = 0
    ref = data.variables["Reflectivity"].values[0, :]
    print(data.variables["Reflectivity"].values.shape)
    rng = data.variables["distanceR"].values[:]
    az = data.variables["azimuthR"].values[0, :]
    az = az[:, None]
    ele = data.variables["elevationR"].values[0, :]
    ele = ele[:, None]

    cx, cy, cz = pyart.core.antenna_to_cartesian(rng / 1000, az, ele)
    lla = pyart.core.cartesian_to_geographic_aeqd(cx, cy, lon, lat, R=6370997.0)

    return (
        lla,
        ref,
        data.time_coverage_start,
        data.StationLongitude,
        data.StationLatitude,
    )
