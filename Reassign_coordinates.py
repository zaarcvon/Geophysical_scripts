import numpy as np
from shapely.geometry import LineString
from segysak.segy import segy_loader, segy_writer, segy_header_scan
import geopandas as gpd
import matplotlib.pyplot as plt

segy_file = "Profile_19.sgy"
###Scan header and show only fields where  meaningful data exists
scan = segy_header_scan(segy_file)
scan[scan["std"] > 0]

seismic_profile = segy_loader(segy_file, cdp=21) 
plt.imshow(seismic_profile.data.T, cmap = 'seismic')

###Read shapefile
shapefile = "profiles.shp"
gdf = gpd.read_file(shapefile)

###Take only one specified polyline from the shapefile
line = gdf.query('N_PROF == "PR_19"').iloc[0].geometry

###Plot the line by its x and y coordinates
plt.plot(line.coords.xy[0],line.coords.xy[1])

###Get number of cdps in seismic file
CDP_amount = seismic_profile.dims['cdp']

###Calculate alongprofile position of CDPs with equal spaces among them
distances = np.linspace(0, line.length, CDP_amount)

###Create new line based on equally spaced vertices along the initial line
CDPs_coords = LineString([ line.interpolate(dist) for dist in distances])

###Append XY coordinates of the vertices to the seismic data
seismic_profile = seismic_profile.assign_coords({'cdp_x':('cdp', CDPs_coords.xy[0])})
seismic_profile = seismic_profile.assign_coords({'cdp_y':('cdp', CDPs_coords.xy[1])})

###Save seismic to a file
output_file = 'seismic_with_coords.sgy'
trace_pos = {'cdp':21, 'cdp_x':73, 'cdp_y':77}
segy_writer(seismic_profile, output_file, trace_header_map = trace_pos)

###Read the header again
scan = segy_header_scan(output_file)
scan[scan["std"] > 0]

