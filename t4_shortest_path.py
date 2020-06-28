import json

import networkx as nx
import rasterio
import geopandas as gpd
from shapely.geometry import LineString

solent_itn_json_path = 'Material/itn/solent_itn.json'
elevation_path = 'Material/elevation/SZ.asc'


def elevation_para_set(elevation):
    """Get some parameters of raster map of elevation for later use.

    :param elevation:
        This object can be the data read by rasterio.open()
    :return: list
        List of the parameters of elevation: minimum x of elevation,
        minimum y of elevation, width of each pixel, height of each pixel
    """
    para_dic = {}
    row_num = elevation.shape[0]
    col_num = elevation.shape[1]
    elevation_left = elevation.bounds[0]
    elevation_bottom = elevation.bounds[1]
    elevation_right = elevation.bounds[2]
    elevation_top = elevation.bounds[3]
    row_pixel_width = (elevation_right - elevation_left)/row_num
    col_pixel_width = (elevation_top - elevation_bottom)/col_num
    para_dic['min_x'] = elevation_left
    para_dic['min_y'] = elevation_bottom
    para_dic['x_bin_width'] = row_pixel_width
    para_dic['y_bin_width'] = col_pixel_width
    return para_dic


def get_elevation(point, elevation_mat, elevation_para):
    """Get the elevation value of the given location.

    :param point: tuple(x, y)
        This is the coordinate of point.
    :param elevation_mat: matrix
        This is the matrix of elevation read from raster map
    :param elevation_para: dictionary
        The parameter set get from elevation_para_set(elevation)
    """
    x = point[0]
    y = point[1]
    row_id = int((x-elevation_para['min_x'])/elevation_para['x_bin_width'])
    col_id = int((y-elevation_para['min_y'])/elevation_para['y_bin_width'])
    elevation_value = elevation_mat[row_id][col_id]
    return elevation_value


def get_gdf(path, itn_graph, itn_json):
    """Transform path to GeoDataframe.

    :param path: list
        The sequence of fid of nodes constructing the path.
    :param itn_graph: networkx.Graph()
        The is the graph of ITN
    :param itn_json:
        This object is the data load from GeoJSON.
    """
    links = []  # this list will be used to populate the feature id (fid) column
    geom = []  # this list will be used to populate the geometry column

    first_node = path[0]
    road_links = itn_json['roadlinks']
    for node in path[1:]:
        link_fid = itn_graph.edges[first_node, node]['fid']
        links.append(link_fid)
        geom.append(LineString(road_links[link_fid]['coords']))
        first_node = node

    path_gdf = gpd.GeoDataFrame({"fid": links, "geometry": geom})
    return path_gdf


def shortest_path(start_node, end_node):
    """Calculate the shortest path between two nodes

    :param start_node: string
        This is the fid of start node in ITN
    :param end_node: string
        This is the fid of end node in ITN
    """
    # Parameter settings
    walking_speed = 5 / 3.6 * 60  # unit: meter/minute

    # Read elevation data
    elevation = rasterio.open(elevation_path)
    elevation_mat = elevation.read(1)
    elevation_para = elevation_para_set(elevation)

    # Create the graph of ITN
    itn_json_input = open(solent_itn_json_path, 'r')
    itn_json = json.load(itn_json_input)
    itn_graph = nx.Graph()
    road_links = itn_json['roadlinks']

    # Construct the network of ITN.
    # Calculate the weight of each link in both directions.
    # The weight of each link depends on its travel time,
    # which consists of basic walking time and additional time for climb
    for link in road_links:
        walking_time_cost = road_links[link]['length'] / walking_speed
        # Calculate additional time cost for climbing
        add_time_forward = 0
        add_time_backward = 0
        points = road_links[link]['coords']
        previous_point = points[0]
        previous_elevation = get_elevation(previous_point, elevation_mat, elevation_para)
        for point in points[1:]:     # Skip the first point
            curr_elevation = get_elevation(point, elevation_mat, elevation_para)
            if curr_elevation > previous_elevation:   # Ascent
                add_time_forward = add_time_forward + (curr_elevation - previous_elevation)
            elif curr_elevation < previous_elevation:  # Descent
                add_time_backward = add_time_backward + (previous_elevation - curr_elevation)
            previous_elevation = curr_elevation

        # An additional minute is added for every 10 meters of climb
        time_cost_forward = walking_time_cost + add_time_forward/10
        time_cost_backward = walking_time_cost + add_time_backward/10

        itn_graph.add_edge(road_links[link]['start'], road_links[link]['end'], fid=link, weight=time_cost_forward)
        itn_graph.add_edge(road_links[link]['end'], road_links[link]['start'], fid=link, weight=time_cost_backward)

    # Calculate the shortest path
    path = nx.dijkstra_path(itn_graph, source=start_node, target=end_node, weight="weight")

    # Create the GeoDataFrame of the shortest path
    shortest_path_gdf = get_gdf(path, itn_graph, itn_json)

    return shortest_path_gdf
