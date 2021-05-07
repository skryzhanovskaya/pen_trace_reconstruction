#
# Created by skryzhanovskaya (skryzhanovskaya@yandex.ru)
#


import networkx as nx
import math
from collections import deque

from trace_reconstruction.strokes import *


class SkeletonGraph:
    def __init__(self, nodes, edges):
        self.nx_graph = self.build_skeleton_graph(nodes, edges)

        self.final_nodes = [node for (node, degree) in self.nx_graph.degree() if degree == 1]
        self.conjunctions = [node for (node, degree) in self.nx_graph.degree() if degree > 2]

        connected_components = list(nx.connected_components(self.nx_graph))
        self.connected_components = self.sort_connected_components(connected_components)

        self.v2cc = {v: i for i, cc in enumerate(self.connected_components) for v in cc}

        if len(self.conjunctions) != 0 or len(self.final_nodes) != 0:
            self.branch_nodes = set(self.conjunctions + self.final_nodes)
        else:
            self.branch_nodes = [0]

        self.branches = self.split_on_branches()

    def split_on_branches(self):   
        
        def find_branch(start_v, cur_v, prev_v, branch):
            if cur_v in self.branch_nodes and cur_v != prev_v:
                if start_v < cur_v:
                    branches.append(branch)
                if start_v == cur_v:  # find cycle
                    flag = True
                    for b in branches:
                        if set(branch) == set(b):
                            flag = False
                            break
                    if flag:
                        branches.append(branch)
            else:
                for u in self.nx_graph.adj[cur_v]:
                    if u != prev_v:
                        find_branch(start_v, u, cur_v, branch + [u])
        branches = []
        
        for v in self.branch_nodes:
            find_branch(v, v, v, [v])
           
        return branches

    @staticmethod
    def build_skeleton_graph(nodes, edges):
        graph = nx.Graph()
        
        for i, node in enumerate(nodes):
            graph.add_node(i, x=node[0], y=node[1])
        
        for edge in edges:
            v1 = edge[0]
            v2 = edge[1]
            edge_len = math.sqrt((graph.nodes[v1]['x'] - graph.nodes[v2]['x']) ** 2 + 
                                 (graph.nodes[v1]['y'] - graph.nodes[v1]['y']) ** 2)
            graph.add_edge(v1, v2, len=edge_len)

        return graph

    def sort_connected_components(self, connected_components):
        min_x_coords = []
        for cc in connected_components:
            x_coords = [self.nx_graph.nodes[v]['x'] for v in cc]
            min_x_coords += [min(x_coords)]

        components = list(zip(connected_components, min_x_coords))
        sorted_components = sorted(components, key=lambda p: p[1])
        sorted_components = [cc[0] for cc in sorted_components]
        return sorted_components


class TraceReconstructor:
    def __init__(self, nodes, edges):
        self.skeleton_graph = SkeletonGraph(nodes, edges)
        self.strokes = self.find_strokes()
        self.meta_graph = self.build_meta_graph()
   
    def build_meta_graph(self):
        meta_graph = nx.Graph()

        for s in self.strokes:
            meta_graph.add_node(s) 

        for i in range(len(self.strokes)):
            s1 = self.strokes[i]
            for j in range(i + 1, len(self.strokes)):
                s2 = self.strokes[j]
                if len(set(s1.trace_path) & set(s2.trace_path)) != 0:
                    meta_graph.add_edge(s1, s2)

        return meta_graph 

    def find_strokes(self):
        strokes = []
        strokes += find_cyclic_strokes(self.skeleton_graph)
        strokes += find_vertical_strokes(self.skeleton_graph)
        strokes += find_semivertical_strokes(self.skeleton_graph, strokes)
        strokes += find_simple_strokes(self.skeleton_graph, strokes)

        return strokes

    def trace(self):

        meta_connected_components = list(nx.connected_components(self.meta_graph))
        meta_connected_components = sorted(meta_connected_components,
                                           key=lambda cc: self.skeleton_graph.v2cc[list(cc)[0].trace_path[0]])
 
        trace = []
        stroke_trace = []
        for meta_cc in meta_connected_components:
            start_stroke = self.find_start_stroke(meta_cc)
            meta_spanning_tree = self.build_spanning_tree(start_stroke)
            cc_stroke_trace = self.stroke_trace(meta_spanning_tree, start_stroke)
            cc_trace = []
            
            for i, stroke in enumerate(cc_stroke_trace):
                previous_strokes = cc_stroke_trace[:i][::-1]

                if len(previous_strokes) == 0:
                    start_node = None

                else:
                    for prev_stroke in previous_strokes:
                        common_nodes = set(stroke.trace_path) & set(prev_stroke.trace_path)
                        if len(common_nodes) != 0:
                            start_node = common_nodes.pop()
                            break
                cc_trace += [stroke.trace(start_node)]
            trace += [cc_trace]
            stroke_trace += [cc_stroke_trace]

        return stroke_trace, trace

    def find_start_stroke(self, meta_strokes):
        skel_nx_graph = self.skeleton_graph.nx_graph
        if len(meta_strokes) == 1:
            return list(meta_strokes)[0]
        
        stroke_dict = {}

        for stroke in meta_strokes:
            if stroke.name == 'cyclic':
                if stroke.level == 3:
                    continue
                else:
                    min_x = min([skel_nx_graph.nodes[v]['x'] for v in stroke.trace_path])
                    stroke_dict[stroke] = min_x         
            else: 
                x = [skel_nx_graph.nodes[v]['x'] for v in stroke.trace_path if v in self.skeleton_graph.final_nodes]
                if len(x) > 0:
                    min_x = min(x)
                    stroke_dict[stroke] = min_x

        assert len(stroke_dict) != 0, "Can't define start stroke"
        start_stroke = sorted(stroke_dict.items(), key=lambda item: item[1])[0][0]
        return start_stroke

    def build_spanning_tree(self, root):
        # взвешенное дерево
        spanning_tree = nx.Graph()
        spanning_tree.add_node(root, weight=root.len)
        queue = deque([root])
        while queue:
            v = queue.popleft()
            for u in self.meta_graph.adj[v]:
                if u not in spanning_tree.nodes:
                    spanning_tree.add_node(u, weight=u.len)
                    spanning_tree.add_edge(v, u)
                    queue.append(u)
        return spanning_tree

    @staticmethod
    def find_maximal_path_weight(meta_graph, s, prev_s):
        max_w = 0
        for next_s in meta_graph.adj[s]:
            if next_s != prev_s:
                w = TraceReconstructor.find_maximal_path_weight(meta_graph, next_s, s)
                max_w = max(w, max_w)
        meta_graph.nodes[s]['max_path_weight'] = max_w + meta_graph.nodes[s]['weight']
        return meta_graph.nodes[s]['max_path_weight'] 

    @staticmethod
    def stroke_trace(meta_graph, start_stroke):
        TraceReconstructor.find_maximal_path_weight(meta_graph, start_stroke, -1)
        
        for stroke in meta_graph.nodes:
            meta_graph.nodes[stroke]['seen'] = False

        trace = []

        stroke = start_stroke
        trace.append(start_stroke)
        meta_graph.nodes[stroke]['seen'] = True
        counter = 1

        while counter != len(meta_graph.nodes):
            next_seen = {next_stroke: meta_graph.nodes[next_stroke]['max_path_weight']
                         for next_stroke in meta_graph.adj[stroke]
                         if meta_graph.nodes[next_stroke]['seen']}
            next_unseen = {next_stroke: meta_graph.nodes[next_stroke]['max_path_weight']
                           for next_stroke in meta_graph.adj[stroke]
                           if not meta_graph.nodes[next_stroke]['seen']}

            if len(next_unseen) == 0:  # return to the previous stroke
                stroke = sorted(next_seen.items(), key=lambda item: item[1], reverse=True)[0][0]

            else:
                stroke = sorted(next_unseen.items(), key=lambda item: item[1])[0][0]
                meta_graph.nodes[stroke]['seen'] = True
                counter += 1
                trace.append(stroke)

        return trace
