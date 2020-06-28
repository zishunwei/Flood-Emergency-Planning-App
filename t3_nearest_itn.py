import json

from rtree import index

solent_itn_json_path = 'Material/itn/solent_itn.json'


def get_nearest_itn_node(point_coords):
    """ Identify the nearest ITN node to the given location

    :param point_coords: tuple(x, y)
        User's location point or the highest point, which is a xy coordinate pair in CRS of British National Grid

    :return: nearest_node：string
        The name of the nearest node like 'osgb4000000026219230'
    """
    # Convert JSON to Rtree
    with open(solent_itn_json_path, 'r') as f:
        solent_itn = json.load(f)
    road_nodes = solent_itn['roadnodes']
    idx = index.Index()
    node_list = []  # Used to find the name of the node based on the number of Rtree
    n = 0
    for node in road_nodes:
        node_coords = road_nodes[node]['coords']
        idx.insert(n, node_coords)
        node_list.append(node)
        n = n + 1

    # Get the nearest ITN node around the location
    # When there is more than one node get found, choose the first one
    nearest_node_indexes = list(idx.nearest(point_coords, 1))
    nearest_node = node_list[nearest_node_indexes[0]]
    return nearest_node
