from typing import List
import tempfile
import subprocess
import os
import collections
import itertools
import json
import networkx as nx

import commons


LOG = commons.make_log(__name__)


class ExternalProcess:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.dir_path = self._dir.name
        self._input = open(os.path.join(self.dir_path, 'input'), 'w')
        self._first = True

    def write_line(self, content):
        '''writes contents to <self.dir_path>/input'''
        if self._first:
            self._first = False
        else:
            self._input.write('\n')
        self._input.write(content)

    def write(self, content):
        '''writes contents to <self.dir_path>/input'''
        self._first = False
        self._input.write(content)

    def read_lines(self, name='output'):
        with open(os.path.join(self.dir_name, name)) as fp:
            for line in fp:
                yield line

    def run(self, command: List[str]):
        self._output = tempfile.NamedTemporaryFile('r')
        self.output_path = self._output.name
        command = [x.replace('__dir__', self.dir_path) for x in command]
        subprocess.run(command)

    def close(self):
        self._dir.cleanup()


class Cluster:
    def __init__(self, multilayer):
        self._graph = multilayer

    def get_cluster_accuracy(self, clusters):
        label = lambda node: self._graph._nodelookup(node)[0]
        counts = [
            collections.Count([label(node) for node in cluster])
            for cluster in clusters
        ]
        import pdb; pdb.set_trace()


    def cluster(self, num_clusters):
        '''uses traditional means to cluster a graph'''
        import pdb; pdb.set_trace()
        G = self._graph.to_networkx()
        comp = nx.algorithms.community.girvan_newman(G)
        clusters = list(itertools.islice(comp, num_clusters))
        return clusters

    def motif_cluster(self, num_clusters):
        snap = commons.settings['external_libs']['snap']
        cmd = os.path.join(snap, 'examples', 'motifs', 'motifs')

        def parse(process, prefix, dict_):
            with open(os.path.join(
                    process.dir_path, 'output-counts.tab')) as fp:
                lines = list(fp.readlines())[1:]
                for line in lines:
                    line = line.rstrip()
                    id_, nodes, edges, count = line.split('\t')
                    dict_[prefix + id_] = \
                        {'nodes': int(nodes),
                         'edges': int(edges),
                         'count': int(count)}
                    
        dict_ = {
            'edges':{'count': sum((2 for _ in self.iter_edges()))},
        }

        if m3:
            process_m3 = self.directed_graph(weighted=False)
            process_m3.run(
                [cmd, '-d=No', '-i:__dir__/input', '-o:__dir__/output', '-m:3'])
            parse(process_m3, 'm3_', dict_)
            process_m3.close()

        if m4:
            process_m4 = self.directed_graph(weighted=False)
            process_m4.run(
                [cmd, '-d=No', '-i:__dir__/input', '-o:__dir__/output', '-m:4'])
            parse(process_m4, 'm4_', dict_)
            process_m4.close()
        pass  # TODO


class Multilayer:
    '''Reads a source file for a multilayer graph and interacts with different
    tools

    Ignored isolated nodes'''
    def __init__(self, path, colors=None):
        self._path = path

        self.edge_colors = None
        self.node_colors = None
        self.node_labels = None

        self._edges = None
        self._nodes = None
        self._node_id_lookup = None
        self._node_label_lookup = None
        self._color_lookup = None

        self._nodelookup_d = None

        if os.path.isfile(path):
            self.loaded = True
            self._load()
        else:
            self.loaded = False
            self._edges = []
            self._nodes = []
            self._node_id_lookup = collections.defaultdict(
                itertools.count().__next__)
            self._node_label_lookup = collections.defaultdict(
                itertools.count().__next__)
            self._color_lookup = collections.defaultdict(
                itertools.count().__next__)

    def add_edge(self, src, tar, color=None, weight=None, time=None):
        src = self._node_id_lookup[src]
        tar = self._node_id_lookup[tar]
        color = self._color_lookup[color]
        edge = (src, tar, color, weight, time)
        assert len(edge) == 5
        self._edges.append(edge)

    def add_node(self, id_, label, color):
        if id_ in self._node_id_lookup:
            return
        self._nodes.append(
            (self._node_id_lookup[id_], label, self._color_lookup[color]))

    def _load(self):
        with open(self._path) as fp:
            data = json.load(fp)

        self._edges = data['edges']
        self._nodes = data['nodes']
        self._node_id_lookup = data['node_id_lookup']
        self._node_label_lookup = data['node_label_lookup']
        self._color_lookup = data['color_lookup']
        for edge in self._edges:
            assert len(edge) == 5

    def set_filters(self, edge_colors=None, node_colors=None,
                    node_labels=None):
        self.edge_colors = edge_colors
        self.node_colors = node_colors
        self.node_labels = node_labels

    def write(self):
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        for edge in self._edges:
            assert len(edge) == 5
        with open(self._path, 'w') as fp:
            json.dump({
                'edges': self._edges,
                'nodes': self._nodes,
                'node_id_lookup': self._node_id_lookup,
                'node_label_lookup': self._node_label_lookup,
                'color_lookup': self._color_lookup
            }, fp)

    def iter_edges(self):
        '''Uses filters set in self.set_filters TODO

        Each edge is src, target, color, weight, time'''
        for edge in self._edges:
            u,v = edge[0], edge[1]
            u_label, u_color =self._nodelookup(u)
            v_label, v_color =self._nodelookup(v)
            if self.node_labels:
                if u_label not in self.node_labels:
                    continue
                if v_label not in self.node_labels:
                    continue
            if self.node_colors:
                if u_color not in self.node_colors:
                    continue
                if v_color not in self.node_colors:
                    continue
            yield edge

    def _nodelookup(self, id_):
        if self._nodelookup_d is None:
            self._nodelookup_d = {i: (l,c) for i,l,c in self._nodes}
            self._color_rev_lookup = \
                    {b:a for a,b in self._color_lookup.items()}
        label,color_id = self._nodelookup_d[id_]
        color = self._color_rev_lookup[color_id]
        return label,color

    def directed_graph_file(self, path, delim='\t', weighted=False,
                            names=False):
        with open(path, 'w') as fp:
            for u, v, c, w, t in self.iter_edges():
                if names:
                    u_label,u_color = self._nodelookup(u)
                    v_label,v_color = self._nodelookup(v)
                    u_label = str(u_label).replace(' ', '_')
                    v_label = str(v_label).replace(' ', '_')
                    u = '{}__label_{}__color_{}'.format(u,u_label,u_color)
                    v = '{}__label_{}__color_{}'.format(v,v_label,v_color)
                else:
                    u,v = str(u), str(v)
                w = str(w)
                if weighted:
                    fp.write(u + delim + v + delim + w + '\n')
                else:
                    fp.write(u + delim + v + '\n')

    def directed_graph(self, delim='\t', weighted=False) -> ExternalProcess:
        process = ExternalProcess()
        self.directed_graph_file(os.path.join(process.dir_path, 'input'),
                            delim='\t', weighted=False)
        return process

    def to_networkx(self):
        '''No time, color, or weight

        Uses self.iter_edges()
        '''
        G = nx.Graph()
        G.add_edges_from(( (u,v) for u,v,c,w,t in self.iter_edges()))
        return G

    @commons.file_cached_class
    def count_motifs(self, path, m3=True, m4=False):
        '''takes a network and a list of motifs to count'''
        snap = commons.settings['external_libs']['snap']
        cmd = os.path.join(snap, 'examples', 'motifs', 'motifs')

        def parse(process, prefix, dict_):
            with open(os.path.join(
                    process.dir_path, 'output-counts.tab')) as fp:
                lines = list(fp.readlines())[1:]
                for line in lines:
                    line = line.rstrip()
                    id_, nodes, edges, count = line.split('\t')
                    dict_[prefix + id_] = \
                        {'nodes': int(nodes),
                         'edges': int(edges),
                         'count': int(count)}
                    
        dict_ = {
            'edges':{'count': sum((2 for _ in self.iter_edges()))},
        }

        if m3:
            process_m3 = self.directed_graph(weighted=False)
            process_m3.run(
                [cmd, '-d=No', '-i:__dir__/input', '-o:__dir__/output', '-m:3'])
            parse(process_m3, 'm3_', dict_)
            process_m3.close()

        if m4:
            process_m4 = self.directed_graph(weighted=False)
            process_m4.run(
                [cmd, '-d=No', '-i:__dir__/input', '-o:__dir__/output', '-m:4'])
            parse(process_m4, 'm4_', dict_)
            process_m4.close()

        with open(path, 'w') as fp:
            json.dump(dict_, fp)


class MutlilayerManager:
    def __init__(self, path):
        self.path = path
        self.colors = MultilayerManager._get_colors(path)

    @staticmethod
    def _get_colors(path):
        m = Multilayer(path)
        colors = set()
        for _, src_color, __, trg_color, ___ in m.iter_read():
            colors.add(src_colors)
            colors.add(trg_colors)
        return colors

    def count_all_motifs(self):
        m = Multilayer(self.path)
        by_color = {}

        by_color['all'] = m.count_motifs()

        for color in self.colors:
            m = Multilayer(self.path, colors=[color])
            by_color[color] = m.count_motifs()

        return by_color


def augment_graph_weights(path, motifs, weights=None):
    '''constructs a weighted graph based on num of motifs edges particate in

    the weight of any particular edge is the sum of the number of times it
    participates in a particular motif times the weight of that motif, for all
    motifs defined.

    By default all motifs have weight one

    Returns an undirected weighted graph
    '''
    passs # TODO
