import os
import urllib
import sys

# check python version
if sys.version_info[0] != 2:
    sys.exit("Must be using Python 2!")

# download data from long/lat grid by looping
# on long and lat

lat_min = 36.5  # starting latitude
lat_max = 47.5  # ending latitude
lat_d = 1.0  # latitude increment step
lng_min = 6.5  # starting longitude
lng_max = 19.5  # ending longitude
lng_d = 1.0  # longitude ending step
data_folder = "data/"  # data folder


# create data folder if missing
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

lat = lat_min
# loop on latitude
while lat <= lat_max:
    lng = lng_min
    # loop on longitude
    while lng <= lng_max:

        # compose file name
        fname = "gridcell_%.1f_%.1f.csv" % (lat, lng)
        fname_out = data_folder + "/" + fname
        print(fname)

        # dowload only if not existing file name
        if not os.path.isfile(fname_out):
            urllib.urlretrieve("https://s3.eu-west-2.amazonaws.com/local-temperature-interactive/data/charts/" + fname, fname_out)
        lng += lng_d
    lat += lat_d

