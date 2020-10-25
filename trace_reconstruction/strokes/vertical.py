#
# Created by skryzhanovskaya (skryzhanovskaya@yandex.ru)
#

import math
from .utils import angle, l1_metric


class VerticalStroke:
    def __init__(self, nx_graph, trace_path, name):
        self.name = name
        self.trace_path = trace_path
        self.len = self.__len(nx_graph, trace_path)
    
    def trace(self, start_node=None):
        if start_node is None:
            return self.trace_path
        else:
            trace_path = self.trace_path[::-1]
            idx = trace_path.index(start_node)
            trace_path = trace_path[idx:] + self.trace_path
            return trace_path            

    def __len(self, nx_graph, trace_path):
        length = 0
        for i in range(len(trace_path)-1):
            v1 = trace_path[i]
            v2 = trace_path[i + 1]
            length += nx_graph.get_edge_data(v1, v2)['len']
        return length

class SemiverticalStroke(VerticalStroke):
    def __init__(self, nx_graph, trace_path):
        super().__init__(nx_graph, trace_path, 'semivertical')


def find_vertical_strokes(skeleton_graph, angle_of_slope=(math.pi / 4, math.pi / 2), l1_criteria=1.5):
    def find_vertical(cur_v, prev_v, start_v, trace_path):
        if cur_v in skeleton_graph.final_nodes and cur_v != start_v:
            v_up = nx_graph.nodes[trace_path[0]]['x'], nx_graph.nodes[trace_path[0]]['y']
            v_down = nx_graph.nodes[trace_path[-1]]['x'], nx_graph.nodes[trace_path[-1]]['y']

            if (v_down[1] > v_up[1] and 
                angle_of_slope[0] <= angle(v_down, v_up) <= angle_of_slope[1]):
                l1 = l1_metric(nx_graph, trace_path)
                if l1 <= l1_criteria:
                    verticals.append((trace_path, l1))
        else:
            for u in nx_graph.adj[cur_v]:
                if u != prev_v and u not in set(trace_path):
                    find_vertical(u, cur_v, start_v, trace_path + [u])
    
    verticals = []
    nx_graph = skeleton_graph.nx_graph

    for v in skeleton_graph.final_nodes:
        find_vertical(v, v, v, [v])

    verticals = sorted(verticals, key=lambda item: item[1])
    verticals = [item[0] for item in verticals]

    covered_nodes = set()
    strokes = []
    
    for trace_path in verticals:
        v_up = trace_path[0]
        v_down = trace_path[-1]
        if v_up not in covered_nodes and v_down not in covered_nodes:
            covered_nodes.add(v_up)
            covered_nodes.add(v_down)
            strokes += [VerticalStroke(nx_graph, trace_path, 'vertical')]

    return strokes


def find_semivertical_strokes(skeleton_graph, other_strokes, angle_of_slope=(math.pi / 4, math.pi / 2), l1_criteria=1.5):
    nx_graph = skeleton_graph.nx_graph
    strokes = []
    covered_branches = set()
    
    for stroke in other_strokes:
        trace_path = stroke.trace_path
        i = 0
        while i < len(trace_path) - 1:
            for j, branch in enumerate(skeleton_graph.branches):
                if (trace_path[i:i + len(branch)] == branch or
                    trace_path[i:i + len(branch)][::-1] == branch):
    
                    covered_branches.add(j)
                    i += len(branch) - 1
                    break

    
    uncovered_branches = set(range(0, len(skeleton_graph.branches))) - covered_branches
    
    for branch in uncovered_branches:
        trace_path = skeleton_graph.branches[branch]

        if ((trace_path[0] in skeleton_graph.final_nodes and trace_path[-1] in skeleton_graph.conjunctions) or 
            (trace_path[-1] in skeleton_graph.final_nodes and trace_path[0] in skeleton_graph.conjunctions)):

            if  trace_path[-1] in skeleton_graph.final_nodes:
                trace_path = trace_path[::-1]
             
            v_up = nx_graph.nodes[trace_path[0]]['x'], nx_graph.nodes[trace_path[0]]['y']
            v_down = nx_graph.nodes[trace_path[-1]]['x'], nx_graph.nodes[trace_path[-1]]['y']

            if (v_down[1] > v_up[1] and 
                angle_of_slope[0] <= angle(v_down, v_up) <= angle_of_slope[1]):
                l1 = l1_metric(nx_graph, trace_path)
                if l1 <= l1_criteria:
                    strokes.append(SemiverticalStroke(nx_graph, trace_path))
         
    return strokes


    