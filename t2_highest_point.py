import numpy as np
import rasterio
import rasterio.plot
from rasterio import mask
from shapely.geometry import Polygon
from shapely.geometry import Point


elevation_path = 'Material/elevation/SZ.asc'


def identify_highest_point(location, radius):
    """ Identify the highest point inside the 5km buffer of given location.

    :param location: tuple(x, y)
        Location input by user, which is a xy coordinate pair in CRS of British National Grid
    :param radius: int or float
        The radius of buffer; use meter as unit

    :return x: float
        The x coordinate of the highest point in CRS of British National Grid.
    :return y: float
        The y coordinate of the highest point in CRS of British National Grid.
    :return local_elevation_array: shapely.geometry.polygon
        The elevation_array clipped by mask.
    :return out_transform:
        Information for mapping pixel coordinates in masked to another coordinate system.
    """
    # Read elevation data and clip it with a 5km buffer whose central point is user's location
    elevation_data = rasterio.open(elevation_path)
    bf = Point(location).buffer(radius)
    elevation_bounds = elevation_data.bounds   # Construct the polygon of the boundary of elevation map
    elevation_boundary = Polygon([(elevation_bounds[0], elevation_bounds[1]),
                                  (elevation_bounds[2], elevation_bounds[1]),
                                  (elevation_bounds[2], elevation_bounds[3]),
                                  (elevation_bounds[0], elevation_bounds[3])])

    mask_polygon = bf.intersection(elevation_boundary)   # Ensure the mask overlaps elevation map
    # Check if area of the mask exists',  which means 5km buffer intersects with elevation map
    if mask_polygon.area != 0:
        local_elevation_array, out_transform = rasterio.mask.mask(dataset=elevation_data, shapes=[mask_polygon],
                                                                  crop=True, filled=False)
        # Find the max value and the location in elevation clipped by mask
        max_elevation = np.max(local_elevation_array)
        location = np.where(local_elevation_array == max_elevation)
        row_highest_point = location[1][0]
        col_highest_point = location[2][0]
        # Transform the row and col to xy coordinates in British National Grid
        x, y = rasterio.transform.xy(out_transform, row_highest_point, col_highest_point)

        return x, y, local_elevation_array, out_transform
    else:  # If mask can't intersects elevation map, return none.
        return None
