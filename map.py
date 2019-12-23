from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from descartes import PolygonPatch
import json
from scipy.interpolate import RegularGridInterpolator
from matplotlib import gridspec
from shapely.geometry import Polygon
from shapely.ops import cascaded_union


obs = "smoothed_anoms"  # observations data
data_folder = "data/"  # data folder
vmin = -1.  # colorbar min range
vmax = 1.5  # colorbar max range
years_min = 1860  # starting age
years_max = 2019  # ending age
ncols = 20  # number of columns in the plot
figsize = (10, 5)  # size of the figure
model = "rcp2.6"  # model for future data
colorscale = "coolwarm"  # color scale for plot

# open json file with geographical data
with open("italy-regions_simple.json") as json_file:
    json_data = json.load(json_file)


data = []
# read data from long/lat temperature sequences
for fname in glob(data_folder + "gridcell_*.csv"):

    # get lat and long from file name
    lat, lng = [float(x) for x in fname.replace(data_folder + "gridcell_","").replace(".csv","").split("_")]

    # loop on file to read data
    for row in open(fname):
        # skip comments
        if row.startswith("\""):
            continue

        # define file header
        labs = [x.strip() for x in "idx, year, obs_anoms, smoothed_anoms, uncertainty, rcp2.6, rcp4.5, rcp6.0, rcp8.5".split(",")]

        # get data from row
        arow = row.strip().split(",")

        # make a dictionary with data
        dd = {lab: arow[i] for i, lab in enumerate(labs)}
        dd["lat"] = float(lat)
        dd["lng"] = float(lng)
        dd["year"] = int(dd["year"])
        dd["fname"] = fname
        data.append(dd)

# get years found
# years = np.unique([dd["year"] for dd in data])

# get data
vals = np.array([[x[lab] for x in data] for lab in ["smoothed_anoms", "rcp2.6", "rcp4.5", "rcp6.0", "rcp8.5"]]).flatten()
vals = np.array([float(x) for x in vals if x != ""])

# only years in the past
years = range(years_min, years_max + 1)

# create figure
fig = plt.figure(figsize=figsize)
# create grid of plots
gs = gridspec.GridSpec(len(years) / ncols, ncols, width_ratios=np.ones(ncols),
         wspace=0.0, hspace=0.0)

# loop on years to plot
for icount, year in enumerate(years):

    print(year)

    # get subplot
    ax = plt.subplot(gs[icount / ncols, icount % ncols])
    # remove axis
    ax.axis('off')

    # prepare polygon geography
    union = []
    for feat in json_data['features']:
        poly = feat['geometry']
        union.append(Polygon(poly["coordinates"][0]))

    # create a union of the regions
    u = cascaded_union(union)
    # generate a patch from union
    patch = PolygonPatch(u, facecolor='none', lw=0)
    # add patch to plot
    ax.add_patch(patch)

    xdata = []
    ydata = []
    zdata = []
    # loop on sorted data
    for dd in sorted(data, key=lambda x: 1000 * x["lng"] + x["lat"]):

        # skip data of different year
        if dd["year"] != year:
            continue

        # find value from observation or model
        if dd[obs] != "":
            val = dd[obs]
        else:
            val = dd[model]

        # warning if missing data
        if val == "":
            print("WARNING: %d replaced value" % year)
            val = val_old

        val_old = val
        xdata.append(dd["lng"])
        ydata.append(dd["lat"])
        zdata.append(float(val))

    # convert to np array
    xdata = np.array(xdata)
    ydata = np.array(ydata)
    zdata = np.array(zdata)

    # find lat and long unique values
    xc = len(np.unique(xdata))
    yc = len(np.unique(ydata))

    # create an interpolator
    f = RegularGridInterpolator((np.unique(xdata), np.unique(ydata)), zdata.reshape(xc, yc), method="linear")

    # generate finer grid
    xnew = np.arange(min(xdata), max(xdata), .1)
    ynew = np.arange(min(ydata), max(ydata), .1)

    # compute interpolation of finer grid
    zdata = f(np.array(np.meshgrid(xnew, ynew)).T).T

    # get lat and long on the finer grid
    xdata, ydata = np.meshgrid(xnew, ynew)

    # get colorscale
    cm_new = cm.get_cmap(colorscale)

    # plot mesh
    pc = ax.pcolor(xdata, ydata, zdata, cmap=cm_new, vmin=vmin, vmax=vmax, clip_path=patch, clip_on=True)

    # trim geographical shape from color mesh
    pc.set_clip_path(patch)

# save to file
plt.tight_layout()
plt.savefig("plot.png", transparent=False, dpi=180)
plt.close(fig)


# save colorbar to file
plt.pcolor(xdata, ydata, zdata, cmap=cm_new, vmin=vmin, vmax=vmax)
cb = plt.colorbar(ticks=[-1, 0, 1, 2, 3, 4], orientation='horizontal')
cb.ax.set_xlabel('Anomalia / $^\circ$C', rotation=0)
plt.savefig("colorbar.png", transparent=False)

