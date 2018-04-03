import luigi
import commons
from commons import file_cached
from os import path
from collections import defaultdict
from itertools import count


class TxtWriter:
    '''Writes txt formats of graphs, which are source_id, target_id, value\n
    '''
    @staticmethod
    @file_cached
    def edges_to_txt(path, edges):
        with open(path, 'w') as fp:
            t = TxtWriter(fp)
            t.add_edges(edges)

    def __init__(self, fp):
        self.mapping = mapping = defaultdict(count().__next__)
        self.fp = fp
        self.first = True

    def add_edge(self, source, target, time):
        if not self.first:
            self.fp.write('\n')
        else:
            self.first = False
        self.fp.write('{} {} {}'.format(
            self.mapping[source], self.mapping[target], time))

    def add_edges(self, edges):
        for edge in edges:
            self.add_edge(*edge)

