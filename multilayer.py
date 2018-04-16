from typing import List
import tempfile
import subprocess
import os

import commons


LOG = commons.makelog(__name__)


class ExternalProcess:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.dir_path = self._dir.name
        self._input = open(os.path.join(self.dir_path, 'input', 'w'))
        self._first = True

    def write_line(self, content):
        '''writes contents to <self.dir_path>/input'''
        if self._first:
            self._first = False
        else:
            self._input.write('\n')
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


class Multilayer:
    '''Reads a source file for a multilayer graph and interacts with different
    tools

    Ignored isolated nodes'''
    def __init__(self, path, colors=None):
        self.path = path
        self.colors = None

    def iter_write(self, edges, fp=None, delim=' '):
        if fp is None:
            with open(self.path, 'w') as fp:
                self.iter_write(edges, fp=fp)
            return

        first = True
        for src, src_color, tar, tar_color, weight in edges:
            if self.colors is not None and \
                        (src_color not in self.colors \
                        or tar_color not in self.colors):
                continue

            if first:
                first = False
            else:
                fp.write('\n')
            this.write(src + delim + src_color + delim + tar + tar_color \
                       + delim + weight)

    def iter_read(self, delim=' '):
        with open(self.path) as fp:
            for line in fp:
                edge = line.split(delim)
                src, src_color, tar, tar_color, weight = edge
                if self.colors is not None and \
                            (src_color not in self.colors \
                            or tar_color not in self.colors):
                    continue
                yield edge

    def directed_graph(self, delim='\t', weighted=True) -> ExternalProcess:
        process = ExternalProcess()
        for s, _, t, __, w in self.iter_read():
            if weighted:
                process.write_line(s + delim + t + delim + w)
            else:
                process.write_line(s + delim + t)
        return process

    def count_motifs(self, path, m3=True, m4=False):
        '''takes a network and a list of motifs to count'''
        snap = commons.settings['external_libs']['snap']
        cmd = os.path.join(snap, 'examples', 'motifs', 'motifs')

        def parse(processs, prefix, dict_):
            with open(os.path.join(
                    process.dir_path, 'output_count.tab')) as fp:
                lines = list(fp.lines())[1:]
                for line in lines:
                    id_, nodes, edges, count = line.split('\t')
                    dict_[prefix + id_] = \
                        {'nodes': nodes, 'edges': edges, 'count': count}
                    
        dict_ = {}
        if m3:
            process_m3 = self.directed_graph(weighted=False)
            process_m3.run(
                [cmd, '-i:__dir__/input', '-o:__dir__/output', '-m:3'])
            parse(process_m3, 'm3_', dict_)
            process_m3.close()

        if m4:
            process_m4 = self.directed_graph(weighted=False)
            process_m4.run(
                [cmd, '-i:__dir__/input', '-o:__dir__/output', '-m:4'])
            parse(process_m3, 'm4_', dict_)
            process_m4.close()

        return dict_

    def cluster(path, num_clusters):
        '''uses traditional means to cluster a graph'''
        pass # TODO

    def motif_cluster(path, num_clusters):
        pass # TODO


class MutlilayerManager:
    def __init__(self, path):
        self.path = path
        self.colors = MultilayerManager._get_colors(path)

    @static_method
    def _get_colors(path):
        m = Multilayer(path)
        colors = set()
        for _, src_color, __, trg_color, ___ in m.iter_read():
            colors.add(src_colors)
            colors.add(trg_colors)
        return colors


    def count_motifs(self):
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
