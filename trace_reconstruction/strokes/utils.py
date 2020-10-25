#
# Created by skryzhanovskaya (skryzhanovskaya@yandex.ru)
#


import math


def angle(a, b):
    x1, y1 = a[0], a[1]
    x2, y2 = b[0], b[1]
    if x1 != x2:
        tan = (y2 - y1) / (x1 - x2)
        return math.atan(tan)
    else:
        return math.pi / 2


def l1_metric(nx_graph, trace_path):
    x1, y1  = nx_graph.nodes[trace_path[0]]['x'], nx_graph.nodes[trace_path[0]]['y']
    x2, y2 = nx_graph.nodes[trace_path[-1]]['x'], nx_graph.nodes[trace_path[-1]]['y']
    a = y2 - y1
    b = x1 - x2
    c = (x2 - x1) * y1 - (y2 - y1) * x1
    dist = 0
    for v in trace_path:
        x = nx_graph.nodes[v]['x']
        y = nx_graph.nodes[v]['y']
        dist += abs(a * x + b * y + c)/ math.sqrt(a**2 + b**2)
    dist /= math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return dist
