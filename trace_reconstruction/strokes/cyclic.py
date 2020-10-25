#
# Created by skryzhanovskaya (skryzhanovskaya@yandex.ru)
#


import numpy as np
import networkx as nx


class CyclicStroke:
    def __init__(self, skeleton_graph, trace_path):
        # trace_path[0] != trace_path[-1] 
        self.name = 'cyclic'
        self.len = self.__len(skeleton_graph.nx_graph, trace_path) 
        self.trace_path = self.__trace_order(skeleton_graph, trace_path)
        self.level = self.__define_level(skeleton_graph.nx_graph)


    def trace(self, start_node=None, end_node=None):

        if self.level == 1:
            
            if start_node is None:
                # start with upper node 
                idx = self.trace_path.index(self.v_up)
            else:
                idx = self.trace_path.index(start_node)
            trace_path = self.trace_path[idx:-1] + self.trace_path[:idx + 1]
        
        if self.level == 2:
            # anticlockwise
            if start_node is None:
                # start with down node 
                idx = self.trace_path.index(self.v_left)
            else:
                idx = self.trace_path.index(start_node)
            trace_path = self.trace_path[idx:-1] + self.trace_path[:idx + 1]

        if self.level == 3:
            # clockwise
            self.trace_path =  self.trace_path[::-1] 
            if start_node is None:
                # start with down node 
                idx = self.trace_path.index(self.v_down)
            else:
                idx = self.trace_path.index(start_node)
            trace_path = self.trace_path[idx:-1] + self.trace_path[:idx + 1]

        if end_node is not None:
            idx = trace_path.index(end_node)
            trace_path += trace_path[1:idx + 1]

        return trace_path

    def __len(self, nx_graph, trace_path):
        length = 0
        for i in range(len(trace_path)-1):
            v1 = trace_path[i]
            v2 = trace_path[i + 1]
            length += nx_graph.get_edge_data(v1, v2)['len']
        length += nx_graph.get_edge_data(trace_path[-1], trace_path[0])['len']
        return length

    def __trace_order(self, skeleton_graph, trace_path):
        # traversing the cycle from the leftmost vertex anticlockwise
        nx_graph = skeleton_graph.nx_graph

        v_x = {v : nx_graph.nodes[v]['x'] for v in trace_path}
        v_y = {v : nx_graph.nodes[v]['y'] for v in trace_path}

        v_x = sorted(v_x.items(), key=lambda item: item[1])
        v_y = sorted(v_y.items(), key=lambda item: item[1])

        self.v_left = v_x[0][0]
        self.v_right = v_x[-1][0]
        self.v_up = v_y[0][0]
        self.v_down = v_y[0][0]

        idx = trace_path.index(self.v_left)
        trace_path = trace_path[idx:] + trace_path[:idx]
        
        for v in trace_path:
            if v == self.v_right: # anticlockwise direction
                break
            if v == self.v_up: # clockwise direction
                trace_path = [trace_path[0]] + trace_path[1:][::-1]
                break
        
        for idx, v in enumerate(trace_path):
        	if v in skeleton_graph.branch_nodes:
        		trace_path = trace_path[idx:] + trace_path[:idx+1] 
        		break
        return trace_path


    def __define_level(self, nx_graph):
        y = np.array([nx_graph.nodes[v]['y'] for v in nx_graph.nodes])
        cycle_y_mean = np.array([nx_graph.nodes[v]['y'] for v in self.trace_path]).mean()
        if cycle_y_mean < np.quantile(y, 0.3):
            return 1
        elif cycle_y_mean < np.quantile(y, 0.7):
            return 2
        else:
            return 3


def find_cyclic_strokes(skeleton_graph):
    strokes = []
    basic_cycles = nx.cycle_basis(skeleton_graph.nx_graph)
    for cycle in basic_cycles:
        strokes += [CyclicStroke(skeleton_graph, cycle)]
    return strokes
            