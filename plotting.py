import os
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from models import Tag


WATER_COLOR = '#99ffff'
LAND_COLOR = '0.8'
PADDING = 5.
IMG_OUTPUT_FOLDER = '.plots'


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
    plt.savefig(filename)
    plt.close()
    
    return filename