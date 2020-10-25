#
# Created by skryzhanovskaya (skryzhanovskaya@yandex.ru)
#


class SimpleStroke:
    def __init__(self, nx_graph, trace_path):
        self.name = 'simple'
        self.trace_path = trace_path
        if nx_graph.nodes[trace_path[-1]]['x'] < nx_graph.nodes[trace_path[0]]['x']:
            self.trace_path = self.trace_path[::-1]
        self.len = self.__len(nx_graph, trace_path)

    def trace(self, start_node=None):
        if start_node is None:
            return self.trace_path
        if self.trace_path[0] == start_node:
            return self.trace_path 
        else:
            return self.trace_path[::-1]             

    def __len(self, nx_graph, trace_path):
        length = 0
        for i in range(len(trace_path)-1):
            v1 = trace_path[i]
            v2 = trace_path[i + 1]
            length += nx_graph.get_edge_data(v1, v2)['len']
        return length

def find_simple_strokes(skeleton_graph, other_strokes):
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
        strokes.append(SimpleStroke(nx_graph, trace_path))
         
    return strokes
