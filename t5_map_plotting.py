import numpy as np
import rasterio
import rasterio.plot
import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from shapely.geometry import Polygon
from shapely.geometry import LineString


def create_north_arrow(display_extent):
    """Creat a north arrow for the map as a GeoDataFrame

    :param display_extent: list[left, right, bottom, top]
        The extent displayed on the map, 10km * 10km, whose center is the start point of the shortest path
    :return: north_arrow_gdf: geopandas.GeoDataFrame
        A north arrow having suitable size and position for the map
    """
    # Create the north arrow on the top left corner of the map
    unit = 300  # Unit length for drawing
    x_offset = 2
    y_offset = 2
    nodes = []
    coordinates = [[1, 3], [0, 0], [1, 1], [2, 0], [1, 3],  # Coordinates of LineString
                   [1, 3], [2, 0], [1, 1]]                  # Coordinates of Polygon
    for xy in coordinates:
        x = xy[0]
        y = xy[1]
        min_x = display_extent[0]
        max_y = display_extent[3]

        # Transform x,y to fit the map
        x = (x + x_offset) * unit + min_x
        y = (y - 3 - y_offset) * unit + max_y
        nodes.append((x, y))
    # Create the polygon of north arrow and construct GeoDataFrame
    north_arrow = [LineString(nodes[:5]), Polygon(nodes[5:])]
    north_arrow_gdf = gpd.GeoDataFrame({"fid": ['1', '2'], "geometry": north_arrow})
    return north_arrow_gdf


def map_plot(user_location, highest_point, path_gdf, local_elevation_array, out_transform, clip_mode):
    """Plot a background map 10km * 10km of the surrounding area with path, buffer, a color-bar showing the elevation
       range, a north arrow, a scale bar, and a legend for the user location, highest point and the shortest path.
       Finally it shows a map

    :param user_location: tuple(x, y)
        Location input by user, which is a xy coordinate pair in CRS of British National Grid
    :param highest_point: turple(x,y)
        Location of the highest point identified, which is a xy coordinates pair of the highest point in
        CRS of British National Grid.
    :param path_gdf: geopandas.GeoDataFrame
        A GeoDataFrame for the shortest path
    :param local_elevation_array:  shapely.geometry.polygon
        The elevation_array clipped by buffer.
    :param out_transform:
            Information for mapping pixel coordinates in masked to another coordinate system.
    """
    fig = plt.figure(figsize=(5, 5), dpi=300)  # Create the figure for mapping
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.OSGB())  # Create subplot in figure for mapping
    ax.set_title(label='Flood Emergency Planning', fontdict={'fontsize': 10})

    # Show background
    isle_background = "Material/background/raster-50k_2724246.tif"
    background = rasterio.open(str(isle_background))
    back_array = background.read(1)
    palette = np.array([value for key, value in background.colormap(1).items()])
    background_image = palette[back_array]
    bounds = background.bounds
    extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
    ax.imshow(background_image, origin="upper", extent=extent, zorder=0)

    # Show elevation in 5km buffer of user's location
    rasterio.plot.show(source=local_elevation_array, ax=ax, zorder=1,
                       transform=out_transform, origin="upper", alpha=0.5, cmap=plt.get_cmap('terrain'))

    # Draw color bar
    norm = cm.colors.Normalize(vmax=np.max(local_elevation_array), vmin=np.min(local_elevation_array))
    cb = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=plt.get_cmap('terrain')), ax=ax)
    cb.ax.tick_params(labelsize=6)  # Set the label size of color bar
    cb.ax.set_ylabel(ylabel='elevation(m)', size=6)  # Set the y_label of color bar

    # Show user's location
    ax.scatter(user_location[0], user_location[1], marker='*', c='r', zorder=2, label='User Location', s=16)
    # Show the highest point
    ax.scatter(highest_point[0], highest_point[1], marker='^', c='g', zorder=2, label='Highest Point', s=10)

    # Show shortest path
    path_gdf.plot(ax=ax, edgecolor="blue", linewidth=0.5, zorder=3, label='The Shortest Path')

    # Show legend
    ax.legend(loc='lower right', prop={'size': 5})

    # Set the display extent, whose centre is the start point of the shortest path.
    # Get the coordinate of start node of shortest path.
    xs, ys = path_gdf["geometry"][0].xy
    left = xs[0] - 5000
    right = xs[0] + 5000
    bottom = ys[0] - 5000
    top = ys[0] + 5000
    if clip_mode == 1:  # When user ask for clipping the map exceeding the range of background
        if left < bounds.left:
            left = bounds.left
        if right > bounds.right:
            right = bounds.right
        if bottom < bounds.bottom:
            bottom = bounds.bottom
        if top > bounds.top:
            top = bounds.top
    display_extent = [left, right, bottom, top]
    ax.set_extent(display_extent, crs=ccrs.OSGB())

    # Draw scalar bar
    scale_bar = AnchoredSizeBar(ax.transData,
                                size=2000, label='2 km', loc=3, pad=0.5, borderpad=0.5,
                                color='black', frameon=False, size_vertical=1)
    ax.add_artist(scale_bar)

    # Draw north arrow
    north_arrow_gdf = create_north_arrow(display_extent)
    north_arrow_gdf.plot(ax=ax, color="black", zorder=4, linewidth=0.5)
    ax.annotate(s='N', xy=(display_extent[0] + 300 * 2.4, display_extent[3] - 300 * 6.5))

    plt.show()  # show the figure
