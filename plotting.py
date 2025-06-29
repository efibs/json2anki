import os
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from models import Tag
import geopandas as gpd
from shapely.geometry import Point
import contextily as cx


WATER_COLOR = '#99ffff'
LAND_COLOR = '0.8'
PADDING = 5.
IMG_OUTPUT_FOLDER = '.plots'
MIN_PADDING = 100000
MAX_PADDING = 1000000
PADDING_PERCENTAGE = 0.2


def plot_tag_plain(tag: Tag) -> str:
    
    # create new figure, axes instances.
    fig=plt.figure()
    ax=fig.add_axes([0.1,0.1,0.8,0.8])

    # Get the extremal values
    min_lat = min(map(lambda c: c.latitude, tag.locations)) - PADDING
    max_lat = max(map(lambda c: c.latitude, tag.locations)) + PADDING
    min_lng = min(map(lambda c: c.longitude, tag.locations)) - PADDING
    max_lng = max(map(lambda c: c.longitude, tag.locations)) + PADDING

    # Clip latitudes to [-90, 90]
    min_lat = max(-90., min(90., min_lat))
    max_lat = max(-90., min(90., max_lat))

    # setup mercator map projection.
    m = Basemap(llcrnrlon=min_lng,llcrnrlat=min_lat,urcrnrlon=max_lng,urcrnrlat=max_lat,\
                resolution='l',projection='merc')

    # Draw country and state lines
    m.drawstates(linestyle='dashed', linewidth=.2)
    m.drawcountries(linewidth=1.)
    
    # Color in the continents and bodies of water
    m.fillcontinents(color=LAND_COLOR, lake_color=WATER_COLOR)
    m.drawmapboundary(fill_color=WATER_COLOR)

    # Plot the coordinates as a scatter plot
    lats = list(map(lambda c: c.latitude, tag.locations))
    lons = list(map(lambda c: c.longitude, tag.locations))
    x, y = m(lons,lats)
    m.scatter(x,y,3,marker='o',color=tag.color)

    # Save the plot to an image file
    filename = os.path.join(IMG_OUTPUT_FOLDER, f'{tag.tag_name.replace(' ', '_').replace('/', '_')}.png') 
    plt.savefig(filename, dpi=220, bbox_inches="tight")
    plt.close()
    
    return filename


def plot_tag_map(tag: Tag) -> str:
    
    # create new figure, axes instances.
    fig, ax = plt.subplots(figsize=(8, 8), dpi=200)

    gdf = gpd.GeoDataFrame(geometry=[Point((location.longitude, location.latitude)) for location in tag.locations], crs="EPSG:4326")

    gdf = gdf.to_crs(epsg=3857)

    gdf.plot(ax=ax, figsize=(8,6), color='red', edgecolor=None, markersize=10, alpha=0.5)

    # Set padding to PADDING_PERCENTAGE of the data
    xmin, ymin, xmax, ymax = gdf.total_bounds
    pad_x = PADDING_PERCENTAGE * (xmax - xmin)
    pad_y = PADDING_PERCENTAGE * (ymax - ymin)

    # Clip padding
    pad_x = max(MIN_PADDING, min(MAX_PADDING, pad_x))
    pad_y = max(MIN_PADDING, min(MAX_PADDING, pad_y))

    # 2. Set padded limits
    ax.set_xlim(xmin - pad_x, xmax + pad_x)
    ax.set_ylim(ymin - pad_y, ymax + pad_y)

    cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, crs=gdf.crs, zoom='auto')
    ax.set_axis_off()

    # Save the plot to an image file
    filename = os.path.join(IMG_OUTPUT_FOLDER, f'{tag.tag_name.replace(' ', '_').replace('/', '_')}.png') 
    plt.savefig(filename, dpi=300, bbox_inches="tight", transparent=True)
    plt.close()
    
    return filename