import geopandas as gpd
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import ticker
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import rasterio
from cartopy.feature import NaturalEarthFeature
from cartopy.feature import ShapelyFeature
# Define downsampling factor
DOWNSAMPLE_FACTOR = 20

# Define the projections
data_crs = ccrs.AlbersEqualArea(
    central_longitude=-154,
    central_latitude=50,
    standard_parallels=(55, 65)
)

# Create Lambert Conformal projection centered on Canada
map_proj = ccrs.LambertConformal(
    central_longitude=-95,
    central_latitude=50,
    standard_parallels=(49, 77)
)

# Set up the plot
plt.figure(figsize=(15, 10))
ax = plt.axes(projection=map_proj)

# Set map bounds
ax.set_extent([-160, -50, 45, 70], crs=ccrs.PlateCarree())

# Read and downsample the GeoTIFF file
with rasterio.open('/glade/derecho/scratch/danqiongd/wetland_project/research_domain/data/NA_500_ecoLc_rcAGB.tif') as src:
    # Print original dimensions
    print(f"Original dimensions: {src.height} x {src.width}")
    
    # Calculate new dimensions
    new_height = src.height // DOWNSAMPLE_FACTOR
    new_width = src.width // DOWNSAMPLE_FACTOR
    print(f"New dimensions: {new_height} x {new_width}")
    
    agb_data = src.read(1, out_shape=(new_height, new_width))
    
    transform = src.transform * src.transform.scale(
        (src.width / agb_data.shape[1]),
        (src.height / agb_data.shape[0])
    )
    
    height, width = agb_data.shape
    x = np.linspace(transform[2], transform[2] + width * transform[0], width)
    y = np.linspace(transform[5], transform[5] + height * transform[4], height)
    xx, yy = np.meshgrid(x, y)
    
    if src.nodata is not None:
        agb_data = np.where(agb_data == src.nodata, np.nan, agb_data)

print (agb_data)
# Add base features in specified colors
# First add all land as white
ax.add_feature(cfeature.LAND, facecolor='white', zorder=0)

# Add ocean as lightblue
ax.add_feature(cfeature.OCEAN, facecolor='lightblue', zorder=1)

# Create and add Canada feature in light grey
#canada = NaturalEarthFeature(
#    category='cultural',
#    name='admin_0_countries',
#    scale='50m'
#)
canada = gpd.read_file('/glade/derecho/scratch/danqiongd/wetland_project/research_domain/canada_shape/geo_can_test.shp')
#canada = ShapelyFeature(canada.geometry,
#                               crs=ccrs.PlateCarree(),
#                               edgecolor='black',
#                               facecolor='lightgrey',
#                               linewidth=0.5)
###ax.add_feature(canada, edgecolor='blue', facecolor = 'lightgrey',linewidth=0.5, zorder=2)
#ax.add_feature(canada,zorder=2)
#canada.plot(ax=ax,
#           edgecolor='blue',
#           facecolor='lightgrey',
##           linewidth=0.5,
#           zorder=2,
#           transform=ccrs.PlateCarree())

# Add lakes in blue
ax.add_feature(cfeature.LAKES.with_scale('50m'), facecolor='royalblue', edgecolor='none', zorder=2)

# Add coastlines and borders
ax.coastlines(resolution='50m', zorder=3)
ax.add_feature(cfeature.BORDERS.with_scale('50m'), linestyle='-', linewidth=0.5, zorder=3)

# Create custom colormap for biomass
colors = [ '#e5f5e0', '#c7e9c0', '#a1d99b', 
          '#74c476', '#41ab5d', '#238b45', '#006d2c']
cmap = mpl.colors.LinearSegmentedColormap.from_list('biomass', colors)

# Calculate data range
valid_data = agb_data[~np.isnan(agb_data)]
vmin, vmax = np.percentile(valid_data, [2, 98])
print(f"Data range: {vmin:.2f} to {vmax:.2f}")
mask_agb_0 = np.isclose(valid_data, 0, rtol=1e-10)
print (mask_agb_0.shape)
agb_display = np.copy(agb_data) # Make a 2D copy
agb_display[np.isnan(agb_data)] = np.nan # Set invalid values to nan, maintains 2D
# Create 2D mask for zero values
mask_agb_0 = np.isclose(agb_display, 0, rtol=1e-10) # This will be 2D
# Process non-zero values while keeping 2D structure
agb_value = np.copy(agb_display)
agb_value[mask_agb_0] = np.nan # This maintains 2D structure
agb_value_0 = agb_value[~np.isnan(agb_value)] #just one dimension, flatten
vmin1, vmax1 = np.percentile(agb_value_0, [2, 98])
print (agb_value.shape,agb_display.shape)
print(f"Data range: {vmin1:.2f} to {vmax1:.2f}")
main_data = np.copy(agb_data)
main_data[~mask_agb_0] = np.nan
main_data[np.isnan(agb_data)] = np.nan
main_value = main_data[~np.isnan(main_data)]
vmin2, vmax2 = np.percentile(main_value, [2, 98])
print(f"Data range: {vmin2:.2f} to {vmax2:.2f}")
print (main_data.shape)

print("Initial data shape:", agb_data.shape)
print("Number of zeros:", np.sum(np.isclose(agb_data, 0, rtol=1e-10)))
print("Number of NaN:", np.sum(np.isnan(agb_data)))
print("Total number of cells:", agb_data.size)

# After creating mask:
print("Mask shape:", mask_agb_0.shape)
print("Number of True in mask:", np.sum(mask_agb_0))

# After creating zero_data:
print("Number of non-NaN in zero_data:", np.sum(np.isnan(main_data)))

#im.set_clim(vmin=2, vmax=120)
# Plot the biomass data
im = ax.pcolormesh(xx, yy, agb_value, 
                   transform=data_crs,
                   cmap=cmap,
                   vmin=2, 
                   vmax=120,
                   shading='auto',
                   zorder=5)



im_grey = ax.contourf(xx, yy, main_data,
                      transform=data_crs,
                      levels=[0, 0.1],  # Only showing values between 0 and 0.1
                      colors=['darkgrey'],
                      zorder=5)

# Add pentagram at specified location
pentagram_lon = -121.3  # 121°18'W
pentagram_lat = 61.3    # 61°18'N

ax.plot(pentagram_lon, pentagram_lat,
        marker='*',
        color='red',
        markersize=20,
        markeredgecolor='black',
        markeredgewidth=1,
        transform=ccrs.PlateCarree(),
        zorder=6)

# Add simple gridlines
gl = ax.gridlines(draw_labels=False, linestyle='--', alpha=0.5, zorder=5)

# Create the colorbar axes inside the main figure
#cbaxes = inset_axes(ax,
#                   width="20%",     # width of colorbar
#                   height="40%",   # height of colorba
#                   bbox_to_anchor=(0.80, 0.70, 0.5, 0.5)
#                   ,bbox_transform=ax.transAxes)
# Add colorbar and title
cbar = plt.colorbar(im, ax= ax, orientation='vertical', 
                  fraction=0.15,  # Make the colorbar thinner
                   shrink=0.5)      # Shorten the colorbar length
cbar.set_label('Aboveground Biomass (Mg/ha)', size=10)

# Set tick label size
cbar.ax.tick_params(labelsize=10)

# Set colorbar limits
#im.set_clim(vmin=2, vmax=120)

# Set number of ticks
cbar.locator = ticker.MaxNLocator(2)  # 5 ticks
cbar.update_ticks()

# Custom tick positions and labels
cbar.set_ticks([2, 120])
cbar.set_ticklabels(['2', '120'])

# Change colorbar width
#cbar.ax.set_aspect(20)

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='grey', label='no tree'),Patch(facecolor='royalblue', label='Lake')]
ax.legend(handles=legend_elements, labels=['no tree', 'Lake'],loc='lower right')


#plt.title('Boreal Forest Aboveground Biomass in Canada', size=12, pad=10)

# Save the figure
plt.savefig('canada_agb_map_test2.png', dpi=300, bbox_inches='tight', metadata=None)
plt.close()
