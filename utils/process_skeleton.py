#
# Created by skryzhanovskaya (skryzhanovskaya@yandex.ru)
#

def process_skeleton(skeleton_path):
    """
    arguments:
        skeleton_path - file with skeleton,
                   each line contains 4 float coordinates x1, y1, x2, y2 for an edge ((x1, y1), (x2, y2))
    returns:
        nodes - list of nodes, node - (x, y)
        edges - list of edges, edge - (v1, v2)
    """

    with open(skeleton_path, 'r') as f:
        skeleton = [[float(x) for x in edge.split()] for edge in f.read().splitlines()]

    nodes = {}
    edges = []

    for edge in skeleton:
        v1 = edge[0], edge[1]
        v2 = edge[2], edge[3]

        if v1 != v2:
            if v1 not in nodes:
                nodes[v1] = len(nodes)
            if v2 not in nodes:
                nodes[v2] = len(nodes)
            edges += [(nodes[v1], nodes[v2])]

    nodes = [item[0] for item in sorted(nodes.items(), key=lambda item: item[1])]

    return nodes, edges
