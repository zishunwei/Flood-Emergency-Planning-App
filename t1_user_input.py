import geopandas as gpd
from shapely.geometry import Point
from pyproj import Transformer


def coordinate_transform(crs, coordinate):
    """Transform the coordinate from WGS84 to British National Grid when the input of user is in CRS of WGS84.

    :param crs: string
        The crs that user choose for input coordinate.
    :param coordinate: tuple(x, y)
        The x,y coordinate user input in CRS of WGS84 or British National Grid
    :return: tuple(x, y)
        Return the coordinate in CRS of British National Grid
    """
    if crs == 'WGS84':
        transfomer = Transformer.from_crs("EPSG:4326", "EPSG:27700")
        coordinate = transfomer.transform(coordinate[0], coordinate[1])
        print(coordinate)
    return coordinate


def check_coordinate(coordinate):
    """Check whether the coordinate from user is within the box (430000, 80000) and (465000, 95000)
    and whether it is on the Isle of Wight respectively.
    The result of the later will return True or False, when the result of the former only be printed on the console.

    :param coordinate: tuple(x, y)
        the coordinates in CRS of British National Grid
    :return: True or False
    """
    if 430000 <= coordinate[0] <= 465000 and 80000 <= coordinate[1] <= 95000:
        print('The coordinate is within the box (430000, 80000) and (465000, 95000)')
    else:
        print('The coordinate is outside the box (430000, 80000) and (465000, 95000)')

    # Check whether the point is on the island
    island_shp_path = 'Material/shape/isle_of_wight.shp'
    island_gdf = gpd.read_file(island_shp_path)
    if Point(coordinate).within(island_gdf['geometry'][0]) or Point(coordinate).touches(island_gdf['geometry'][0]):
        print('Your location is on the Isle of Wight')
        return True
    else:
        print('No service outside the Isle of Wight')
        return False


def get_user_input():
    """Get the user input, and check them by check_coordinate(coordinate) function
    """
    x = int(input("Please input the coordinate x:"))
    y = int(input('Please input the coordinate y:'))
    if check_coordinate((x, y)):
        print("This coordinate is valid!")
        return x, y
    else:
        print("This coordinate is invalid! quit this application...")
        return None


if __name__ == "__main__":
    # For Unit Test
    print(get_user_input())
